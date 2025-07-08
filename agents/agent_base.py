# agent_base.py

import os
import json
import logging
import requests
import traceback
from abc import ABC, abstractmethod
import openai
try:
    import anthropic
except ImportError:  # pragma: no cover - optional dependency
    anthropic = None
from typing import Any, Dict, Optional

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in The Agency.
    Handles LLM interaction via OpenAI or Ollama.
    """

    def __init__(self, config: Any, memory: Any):
        """
        Initialize the base agent with configuration and memory.

        Args:
            config: Configuration object with API keys and model settings.
            memory: Memory object for saving and retrieving information.
        """
        if not hasattr(config, "GPT4_API_KEY") or not hasattr(config, "OLLAMA_API_URL"):
            raise ValueError("Config must contain 'GPT4_API_KEY' and 'OLLAMA_API_URL'")

        self.config = config
        self.memory = memory

        key = getattr(config, "GPT4_API_KEY", "")
        if not key or key.startswith("your-"):
            logger.warning(
                "GPT4_API_KEY is not set or is using the placeholder value. "
                "OpenAI features will be disabled until a valid key is provided."
            )
            self.openai_client = None
        else:
            self.openai_client = openai.OpenAI(api_key=key)

        akey = getattr(config, "ANTHROPIC_API_KEY", "")
        if anthropic and akey:
            self.anthropic_client = anthropic.Anthropic(api_key=akey)
        else:
            self.anthropic_client = None

    @abstractmethod
    def generate_plan(self, user_prompt: str):
        """
        Abstract method to be implemented by child agents.

        Args:
            user_prompt (str): The input prompt from the user.

        Returns:
            Any: Implementation-specific plan or result.
        """
        pass

    def call_llm(self, prompt: str, model: str = "gpt-4", system: str = "") -> str:
        """
        Unified method for calling either GPT or Ollama models.

        Args:
            prompt (str): User input or task description.
            model (str): Model name (e.g., 'gpt-4o' or 'qwen:7b').
            system (str): Optional system-level instruction for context.

        Returns:
            str: The generated model response.
        """
        model = model.strip().lower()
        logger.info(f"🧠 Calling LLM → Model: {model}")

        if model.startswith("gpt"):
            return self._call_openai_chat(model, prompt, system)
        if model.startswith("claude") or model.startswith("anthropic"):
            return self._call_anthropic_chat(model, prompt, system)
        return self._call_ollama_chat(model, prompt, system)

    def _call_openai_chat(self, model: str, user_prompt: str, system_prompt: str = "") -> str:
        """
        Calls OpenAI's chat model.

        Returns:
            str: Assistant message or error.
        """
        if not self.openai_client:
            logger.error("❌ OpenAI client is not configured. Set GPT4_API_KEY to use this feature.")
            return "❌ OpenAI client not configured"

        messages = self._build_messages(user_prompt, system_prompt)
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"❌ OpenAI error: {e}\n{error_details}")
            return f"❌ OpenAI error: {e}"

    def _call_anthropic_chat(self, model: str, user_prompt: str, system_prompt: str = "") -> str:
        """Calls Anthropic's chat API."""
        if not self.anthropic_client:
            logger.error("❌ Anthropic client is not configured. Set ANTHROPIC_API_KEY to use this feature.")
            return "❌ Anthropic client not configured"

        messages = self._build_messages(user_prompt, system_prompt)
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1024,
                messages=messages,
            )
            if hasattr(response, "content"):
                return "".join(block.text for block in response.content).strip()
            return str(response)
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"❌ Anthropic error: {e}\n{error_details}")
            return f"❌ Anthropic error: {e}"

    def _call_ollama_chat(self, model: str, user_prompt: str, system_prompt: str = "") -> str:
        """
        Calls a local Ollama model via REST API.

        Returns:
            str: Assistant message or error.
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": self._build_messages(user_prompt, system_prompt),
            "stream": False,
        }

        timeout = getattr(self.config, "REQUEST_TIMEOUT", 60)

        url = self.config.OLLAMA_API_URL.rstrip("/")
        if not url.endswith("/api/chat") and not url.endswith("/api/generate"):
            url = f"{url}/api/chat"

        try:
            res = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            res.raise_for_status()
            try:
                result = res.json()
            except Exception:
                # Handle streaming or malformed JSON by concatenating lines
                text = res.text.strip()
                parts = []
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            parts.append(data["message"]["content"])
                    except json.JSONDecodeError:
                        continue
                return "".join(parts).strip()

            # Ollama v1 format
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()

            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"❌ Ollama error: {e}\n{error_details}")
            return f"❌ Ollama error: {e}"

    def _build_messages(self, user_prompt: str, system_prompt: str = "") -> list:
        """
        Helper to build LLM message list.

        Args:
            user_prompt (str): The user’s prompt.
            system_prompt (str): Optional system instruction.

        Returns:
            list: Message list formatted for chat models.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return messages
