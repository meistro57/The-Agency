# agent_base.py

import os
import json
import requests
from abc import ABC, abstractmethod
import openai

class BaseAgent(ABC):
    def __init__(self, config, memory):
        self.config = config
        self.memory = memory

        if hasattr(config, "GPT4_API_KEY") and config.GPT4_API_KEY:
            self.openai_client = openai.OpenAI(api_key=config.GPT4_API_KEY)
        else:
            self.openai_client = None

    @abstractmethod
    def generate_plan(self, user_prompt: str):
        pass

    def call_llm(self, prompt: str, model: str = "gpt-4", system: str = "") -> str:
        model = model.lower().strip()
        print(f"🧠 Calling LLM → Model: {model}")

        if model.startswith("gpt"):
            if not self.openai_client:
                return "❌ No OpenAI client configured."
            return self._call_openai_chat(model, prompt, system)
        else:
            return self._call_ollama_chat(model, prompt, system)

    def _call_openai_chat(self, model, user_prompt, system_prompt="") -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return f"❌ OpenAI error: {e}"

    def _call_ollama_chat(self, model, user_prompt, system_prompt="") -> str:
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": []
            }

            if system_prompt:
                payload["messages"].append({"role": "system", "content": system_prompt})
            payload["messages"].append({"role": "user", "content": user_prompt})

            res = requests.post(
                url=self.config.OLLAMA_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            res.raise_for_status()
            result = res.json()

            # Ollama's new response format
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()

            # Fallback for older formats
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return f"❌ Ollama error: {e}"
