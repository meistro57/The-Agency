# tester.py

from agents.agent_base import BaseAgent
import os
import subprocess

class TesterAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Test Runner"
        self.description = "Executes Python files to detect runtime errors"

    def generate_plan(self, user_prompt: str):
        # Dummy method to satisfy abstract base class
        return {}

    def run_tests(self, file_paths: list) -> dict:
        print(f"\n🧪 [{self.role}] Running tests on generated files...")
        results = {}

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            if not full_path.endswith(".py") or not os.path.exists(full_path):
                results[path] = "✅ Skipped (not a Python file)"
                continue

            try:
                output = subprocess.check_output(
                    ["python3", full_path],
                    stderr=subprocess.STDOUT,
                    timeout=10
                )
                results[path] = "✅ Passed\n" + output.decode()
            except subprocess.CalledProcessError as e:
                results[path] = f"❌ Runtime error:\n{e.output.decode()}"
            except subprocess.TimeoutExpired:
                results[path] = "❌ Timed out"
            except Exception as e:
                results[path] = f"❌ Unexpected error: {str(e)}"

            self.memory.save(f"test_result::{path}", results[path])

        print("✅ Testing complete.")
        return results
