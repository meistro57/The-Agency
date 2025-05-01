# agent_base.py

import requests
import openai
import os
import json

class BaseAgent:
    def __init__(self, config, memory):
        self.config = config
        self.memory = memory
        self.session_log = []

    def call_llm(self, prompt, model="ollama", system="You are an AI assistant."):
        """
        Call the selected LLM (either local Ollama or OpenAI GPT-4) with a system+user prompt.
        """
        if model == "ollama":
            return self._call_ollama(prompt, system)
        elif model == "gpt4":
            return self._call_gpt4(prompt, system)
        else:
            raise ValueError(f"Unsupported model: {model}")

    def _call_ollama(self, prompt, system):
        try:
            payload = {
                "model": self.config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            response = requests.post(
                self.config.OLLAMA_API_URL + "/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ Ollama call failed: {e}")
            return ""

    def _call_gpt4(self, prompt, system):
        try:
            openai.api_key = self.config.GPT4_API_KEY
            response = openai.ChatCompletion.create(
                model=self.config.GPT4_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ GPT-4 call failed: {e}")
            return ""

    def log(self, message: str):
        print(message)
        self.session_log.append(message)
