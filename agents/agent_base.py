# Improved agent_base.py with better error handling and retry logic

import os
import json
import logging
import requests
import traceback
import time
from abc import ABC, abstractmethod
import openai
try:
    import anthropic
except ImportError:
    anthropic = None
from typing import Any, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in The Agency.
    Handles LLM interaction via OpenAI, Anthropic, or Ollama with retry logic.
    """

    def __init__(self, config: Any, memory: Any):
        """Initialize the base agent with configuration and memory."""
        if not hasattr(config, "OLLAMA_API_URL"):
            raise ValueError("Config must contain 'OLLAMA_API_URL'")

        self.config = config
        self.memory = memory
        self.max_retries = getattr(config, "MAX_RETRIES", 3)
        self.retry_delay = getattr(config, "RETRY_DELAY", 2)

        # Initialize OpenAI client
        key = getattr(config, "GPT4_API_KEY", "")
        if key and not key.startswith("your-"):
            self.openai_client = openai.OpenAI(api_key=key)
        else:
            logger.warning("OpenAI API key not configured")
            self.openai_client = None

        # Initialize Anthropic client
        akey = getattr(config, "ANTHROPIC_API_KEY", "")
        if anthropic and akey and not akey.startswith("your-"):
            self.anthropic_client = anthropic.Anthropic(api_key=akey)
        else:
            self.anthropic_client = None

        # Test Ollama connection
        self._test_ollama_connection()

    def _test_ollama_connection(self):
        """Test if Ollama is reachable."""
        try:
            url = self.config.OLLAMA_API_URL.rstrip("/")
            test_url = url if "/api/" in url else f"{url}/api/tags"
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama connection successful")
            else:
                logger.warning(f"⚠️ Ollama returned status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Cannot connect to Ollama at {self.config.OLLAMA_API_URL}: {e}")
            logger.info("💡 Make sure Ollama is running with 'ollama serve'")

    @abstractmethod
    def generate_plan(self, user_prompt: str):
        """Abstract method to be implemented by child agents."""
        pass

    def call_llm(self, prompt: str, model: str = "gpt-4", system: str = "") -> str:
        """
        Unified method for calling LLMs with retry logic and fallbacks.
        
        Args:
            prompt (str): User input or task description.
            model (str): Model name (e.g., 'gpt-4o', 'qwen:7b', 'claude-3-sonnet').
            system (str): Optional system-level instruction for context.

        Returns:
            str: The generated model response.
        """
        model = model.strip().lower()
        logger.info(f"🧠 Calling LLM → Model: {model}")

        # Try the primary model with retries
        for attempt in range(self.max_retries):
            try:
                if model.startswith("gpt"):
                    return self._call_openai_chat(model, prompt, system)
                elif model.startswith("claude") or model.startswith("anthropic"):
                    return self._call_anthropic_chat(model, prompt, system)
                else:
                    return self._call_ollama_chat(model, prompt, system)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
                    return self._get_fallback_response(prompt, model, str(e))

    def _get_fallback_response(self, prompt: str, model: str, error: str) -> str:
        """Generate a fallback response when all LLM calls fail."""
        logger.warning(f"Using fallback response due to error: {error}")
        
        # Try alternative models
        fallback_models = []
        if not model.startswith("gpt") and self.openai_client:
            fallback_models.append("gpt-3.5-turbo")
        if not model.startswith("claude") and self.anthropic_client:
            fallback_models.append("claude-3-haiku-20240307")
        
        for fallback_model in fallback_models:
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                return self.call_llm(prompt, fallback_model, "")
            except Exception:
                continue
        
        # Final fallback: return a structured error response
        return f"❌ LLM Error: {error}\n\nPlease check:\n1. Is Ollama running? (ollama serve)\n2. Is the model pulled? (ollama pull {model})\n3. Are API keys configured correctly?"

    def _call_openai_chat(self, model: str, user_prompt: str, system_prompt: str = "") -> str:
        """Calls OpenAI's chat model."""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not configured")

        messages = self._build_messages(user_prompt, system_prompt)
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _call_anthropic_chat(self, model: str, user_prompt: str, system_prompt: str = "") -> str:
        """Calls Anthropic's chat API."""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not configured")

        messages = self._build_messages(user_prompt, system_prompt)
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=2000,
                messages=messages,
                temperature=0.7
            )
            if hasattr(response, "content"):
                return "".join(block.text for block in response.content if hasattr(block, 'text')).strip()
            return str(response)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _call_ollama_chat(self, model: str, user_prompt: str, system_prompt: str = "") -> str:
        """Calls a local Ollama model via REST API."""
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": self._build_messages(user_prompt, system_prompt),
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2000
            }
        }

        timeout = getattr(self.config, "REQUEST_TIMEOUT", 60)
        
        # Ensure correct API endpoint
        url = self.config.OLLAMA_API_URL.rstrip("/")
        if not url.endswith("/api/chat"):
            url = f"{url}/api/chat"

        try:
            res = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            res.raise_for_status()
            
            result = res.json()
            
            # Handle response format
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()
            elif "response" in result:
                return result["response"].strip()
            else:
                logger.error(f"Unexpected response format: {result}")
                raise ValueError("Invalid response format from Ollama")
                
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {url}. "
                "Make sure Ollama is running with 'ollama serve'"
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise RuntimeError(
                    f"Model '{model}' not found. "
                    f"Pull it first with: ollama pull {model}"
                )
            raise
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise

    def _build_messages(self, user_prompt: str, system_prompt: str = "") -> list:
        """Helper to build LLM message list."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def extract_json_from_response(self, response: str) -> dict:
        """
        Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            response (str): Raw LLM response
            
        Returns:
            dict: Parsed JSON object
        """
        # Remove markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        # Try to find JSON object
        import re
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try full response
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid JSON in response: {e}")
