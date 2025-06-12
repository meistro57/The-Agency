# fixer.py

import os
import logging
from agents.agent_base import BaseAgent
import openai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class FixerAgent(BaseAgent):
    """
    Attempts to automatically fix broken code using GPT-4o based on test output.
    """

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Fixer"
        self.description = "Attempts to automatically fix broken code using GPT-4o"

        if not config.GPT4_API_KEY:
            raise ValueError("❌ GPT-4 API key is missing in the configuration.")

        try:
            self.client = openai.OpenAI(api_key=config.GPT4_API_KEY)
        except Exception as e:
            logging.error(f"❌ Failed to initialize OpenAI client: {e}")
            raise

    def generate_plan(self, user_prompt: str):
        return {}

    def fix_code(self, file_paths: list, test_results: dict) -> dict:
        """
        Fixes code files that have test failures.

        Args:
            file_paths (list): List of relative paths to code files.
            test_results (dict): Dictionary of {path: test_output}.

        Returns:
            dict: Dictionary of {path: fixed_code or error_message}
        """
        if not isinstance(file_paths, list):
            raise ValueError("file_paths must be a list of strings.")
        if not isinstance(test_results, dict):
            raise ValueError("test_results must be a dictionary.")

        logging.info(f"🔧 [{self.role}] Attempting automatic code fixes using GPT-4o...")

        fixes = {}
        fix_cache = {}

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)

            if not os.path.isfile(full_path):
                logging.error(f"❌ File not found: {path}")
                fixes[path] = "❌ File missing"
                continue

            if path in fix_cache:
                logging.info(f"⚡ Using cached fix for {path}")
                fixes[path] = fix_cache[path]
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    original_code = f.read()
            except Exception as e:
                logging.error(f"❌ Failed to read file {path}: {e}")
                fixes[path] = f"❌ File read error: {e}"
                continue

            test_output = test_results.get(path, "")
            prompt = self._build_fix_prompt(path, original_code, test_output)

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a senior developer who fixes broken code."},
                        {"role": "user", "content": prompt}
                    ]
                )
                fixed_code = response.choices[0].message.content.strip()
                fix_cache[path] = fixed_code
                fixes[path] = fixed_code

                try:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(fixed_code)
                    self.memory.save(f"FixerAgent::patch::{path}", fixed_code)
                    logging.info(f"✅ Fixed: {path}")
                except Exception as e:
                    logging.error(f"❌ Failed to write fix to {path}: {e}")
                    fixes[path] = f"❌ Write error: {e}"

            except Exception as e:
                logging.error(f"❌ LLM error while fixing {path}: {e}")
                fixes[path] = f"❌ Fixer error: {e}"

        logging.info("✅ Code fixing complete.")
        return fixes

    def _build_fix_prompt(self, path: str, code: str, test_output: str) -> str:
        """
        Builds a prompt for the LLM to fix the given code file.

        Args:
            path (str): Path of the file being fixed.
            code (str): Current code in the file.
            test_output (str): The result from failed tests.

        Returns:
            str: LLM prompt.
        """
        max_len = 1000
        truncated_code = code if len(code) <= max_len else code[:max_len] + "\n# [Code truncated...]"

        return f"""
The following file contains broken code based on its test results.

Filename: {path}

--- Current Code ---
```python
{truncated_code}
```

--- Test Output ---
{test_output}

Please provide the fixed {path} file only.
"""
