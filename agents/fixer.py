# fixer.py

from agents.agent_base import BaseAgent
import os

class FixerAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Code Fixer"
        self.description = "Applies fixes to code based on test results or QA feedback."

    def repair_files(self, file_paths: list):
        print(f"\n🛠️ [{self.role}] Repairing broken or flagged code...")

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            if not os.path.exists(full_path):
                print(f"⚠️ Missing file: {path}")
                continue

            original_code = self._read_file(full_path)
            test_feedback = self.memory.get(f"test_result::{path}", "")
            qa_feedback = self.memory.get(f"qa_feedback::{path}", "")

            if "✅" in test_feedback and not qa_feedback:
                continue  # no fix needed

            new_code = self._fix_code(path, original_code, test_feedback, qa_feedback)
            if new_code and new_code.strip() != original_code.strip():
                self._write_file(full_path, new_code)
                print(f"✅ Fixed: {path}")
            else:
                print(f"⏭️ No changes made to: {path}")

    def _fix_code(self, file_path: str, code: str, test_feedback: str, qa_feedback: str) -> str:
        prompt = f"""
        A code file has issues identified by testing and QA review.

        File: {file_path}

        Original Code:
        ```python
        {code}
        ```

        Test Feedback:
        {test_feedback}

        QA Feedback:
        {qa_feedback}

        Please rewrite the code with appropriate fixes, maintaining structure and clarity.
        """

        return self.call_llm(prompt, model="ollama", system="You are a bug-fixing agent.")

    def _read_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(self, path, code):
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
