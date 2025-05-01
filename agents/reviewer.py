# reviewer.py

from agents.agent_base import BaseAgent
import os

class ReviewerAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "QA Reviewer"
        self.description = "Performs code review using GPT-4"

    def review_code(self, file_paths: list) -> dict:
        print(f"\n🔍 [{self.role}] Performing GPT-4 code review...")
        reviews = {}

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            if not os.path.exists(full_path):
                reviews[path] = "❌ File missing"
                continue

            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()

            feedback = self._review_with_gpt4(path, code)
            reviews[path] = feedback
            self.memory.save(f"qa_feedback::{path}", feedback)

        print("✅ GPT-4 review complete.")
        return reviews

    def _review_with_gpt4(self, file_path: str, code: str) -> str:
        prompt = f"""
        You are a senior software reviewer. Please analyze the following code for:

        - Bugs or edge cases
        - Code quality and readability
        - Security concerns
        - Recommendations for improvement

        File: {file_path}

        ```python
        {code}
        ```

        Return your analysis in a bullet-point summary.
        """
        return self.call_llm(prompt, model="gpt4", system="You are a meticulous software reviewer.")

    def qa_passed(self, reviews: dict) -> bool:
        for feedback in reviews.values():
            if "❌" in feedback or "fix" in feedback.lower():
                return False
        return True
