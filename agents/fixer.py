# fixer.py

from agents.agent_base import BaseAgent
import os
import openai

class FixerAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Fixer"
        self.description = "Attempts to automatically fix broken code using GPT-4o"
        self.client = openai.OpenAI(api_key=config.GPT4_API_KEY)

    def fix_code(self, file_paths: list, test_results: dict) -> dict:
        print(f"\n🔧 [{self.role}] Attempting automatic code fixes using GPT-4o...")
        fixes = {}

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            if not os.path.exists(full_path):
                fixes[path] = "❌ File missing"
                continue

            with open(full_path, "r", encoding="utf-8") as f:
                original_code = f.read()

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
                fixes[path] = fixed_code

                # Overwrite file with fixed code
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(fixed_code)

                self.memory.save(f"fix_patch::{path}", fixed_code)

            except Exception as e:
                fixes[path] = f"❌ Fixer error: {str(e)}"

        print("✅ Code fixing complete.")
        return fixes

    def _build_fix_prompt(self, path: str, code: str, test_output: str) -> str:
        return f"""
The following code file has errors based on its test results.

Filename: {path}

--- Current Code ---
```python
{code}
    Please return ONLY the updated code. Do not explain it. Make it functional and fix the error above.
"""

