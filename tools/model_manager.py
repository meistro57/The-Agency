# tools/model_manager.py - Intelligent model selection and management

import os
import logging
import requests
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages available models and selects the best one for each task."""
    
    def __init__(self, config):
        self.config = config
        self.available_models = {
            "ollama": [],
            "openai": [],
            "anthropic": []
        }
        self.model_capabilities = {
            # Ollama models
            "qwen:7b": {"type": "ollama", "good_for": ["code", "general"], "quality": 7},
            "qwen:14b": {"type": "ollama", "good_for": ["code", "general"], "quality": 8},
            "codestral:latest": {"type": "ollama", "good_for": ["code"], "quality": 9},
            "mixtral:latest": {"type": "ollama", "good_for": ["general", "reasoning"], "quality": 8},
            "llama3:latest": {"type": "ollama", "good_for": ["general"], "quality": 8},
            
            # OpenAI models
            "gpt-4o": {"type": "openai", "good_for": ["code", "review", "architecture"], "quality": 10},
            "gpt-4-turbo": {"type": "openai", "good_for": ["code", "review"], "quality": 9},
            "gpt-3.5-turbo": {"type": "openai", "good_for": ["general", "fast"], "quality": 7},
            
            # Anthropic models
            "claude-3-opus-20240229": {"type": "anthropic", "good_for": ["code", "review", "complex"], "quality": 10},
            "claude-3-sonnet-20240229": {"type": "anthropic", "good_for": ["code", "general"], "quality": 9},
            "claude-3-haiku-20240307": {"type": "anthropic", "good_for": ["fast", "general"], "quality": 7},
        }
        
        self.refresh_available_models()
    
    def refresh_available_models(self):
        """Check which models are actually available."""
        # Check Ollama models
        self._check_ollama_models()
        
        # Check OpenAI availability
        if hasattr(self.config, "GPT4_API_KEY") and self.config.GPT4_API_KEY and not self.config.GPT4_API_KEY.startswith("your-"):
            self.available_models["openai"] = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        # Check Anthropic availability
        if hasattr(self.config, "ANTHROPIC_API_KEY") and self.config.ANTHROPIC_API_KEY:
            self.available_models["anthropic"] = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307"
            ]
    
    def _check_ollama_models(self):
        """Check which Ollama models are available."""
        try:
            url = self.config.OLLAMA_API_URL.rstrip("/")
            if "/api/" not in url:
                url = f"{url}/api/tags"
            else:
                url = url.replace("/api/chat", "/api/tags")
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                self.available_models["ollama"] = [
                    m["name"] for m in models if "name" in m
                ]
                logger.info(f"Found Ollama models: {self.available_models['ollama']}")
            else:
                logger.warning(f"Failed to list Ollama models: {response.status_code}")
        except Exception as e:
            logger.error(f"Cannot check Ollama models: {e}")
    
    def get_best_model_for_task(self, task_type: str) -> Optional[str]:
        """
        Select the best available model for a given task type.
        
        Args:
            task_type: One of "code", "review", "architecture", "general", "fast"
            
        Returns:
            Best available model name or None
        """
        candidates = []
        
        # Find all models good for this task
        for model_name, info in self.model_capabilities.items():
            if task_type in info["good_for"]:
                model_type = info["type"]
                if model_name in self.available_models.get(model_type, []):
                    candidates.append((model_name, info["quality"]))
        
        # Sort by quality (higher is better)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        if candidates:
            best_model = candidates[0][0]
            logger.info(f"Selected {best_model} for task type: {task_type}")
            return best_model
        
        # Fallback to any available model
        for provider in ["openai", "anthropic", "ollama"]:
            if self.available_models[provider]:
                fallback = self.available_models[provider][0]
                logger.warning(f"No specific model for {task_type}, using fallback: {fallback}")
                return fallback
        
        logger.error(f"No models available for task: {task_type}")
        return None
    
    def pull_ollama_model(self, model_name: str) -> bool:
        """Pull an Ollama model if not already available."""
        import subprocess
        try:
            logger.info(f"Pulling Ollama model: {model_name}")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            if result.returncode == 0:
                logger.info(f"Successfully pulled {model_name}")
                self.refresh_available_models()
                return True
            else:
                logger.error(f"Failed to pull {model_name}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a specific model is available, pulling if necessary."""
        # Check if already available
        for provider, models in self.available_models.items():
            if model_name in models:
                return True
        
        # Try to pull if it's an Ollama model
        if model_name in self.model_capabilities and self.model_capabilities[model_name]["type"] == "ollama":
            return self.pull_ollama_model(model_name)
        
        return False
    
    def get_model_info(self) -> Dict[str, List[str]]:
        """Get information about all available models."""
        return self.available_models
