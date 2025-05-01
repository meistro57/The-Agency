# tester.py

from agents.agent_base import BaseAgent
import subprocess
import os

class TesterAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Test Runner"
        self.description = "Runs tests and captures results"

    def run_tests(self, file_paths: list) -> dict:
        print(f"\n🧪 [{self.role}] Running tests on generated files...")
        results = {}

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            if not os.path.exists(full_path):
                results[path] = "❌ File missing"
                continue

            # Determine how to test this file
            if path.endswith(".py"):
                output = self._run_python_file(full_path)
            else:
                output = f"⚠️ No test strategy defined for {path}"
            
            results[path] = output
            self.memory.save(f"test_result::{path}", output)

        print("✅ Testing complete.")
        return results

    def _run_python_file(self, filepath: str) -> str:
        try:
            proc = subprocess.run(
                ["python", filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                return "✅ Passed\n" + proc.stdout
            else:
                return f"❌ Failed (code {proc.returncode})\n{proc.stderr}"
        except subprocess.TimeoutExpired:
            return "⏱️ Timeout"
        except Exception as e:
            return f"❌ Error: {e}"

    def all_tests_passed(self, results: dict) -> bool:
        return all("✅" in outcome for outcome in results.values())
