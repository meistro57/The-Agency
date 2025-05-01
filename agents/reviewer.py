# reviewer.py

import os
import logging
from concurrent.futures import ThreadPoolExecutor
from agents.agent_base import BaseAgent
import openai
import traceback

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ReviewerAgent(BaseAgent):
    """
    A QA Reviewer Agent that uses GPT-4o to review code files for potential improvements or issues.
    """

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "QA Reviewer"
        self.description = "Performs GPT-4-based code review"
        self.client = openai.OpenAI(api_key=config.GPT4_API_KEY)

    def generate_plan(self, user_prompt: str):
        """Dummy method to satisfy abstract class."""
        return {}

    def review_code(self, file_paths: list) -> dict:
        """
        Review a list of source code files in parallel and return GPT-4o feedback.

        Args:
            file_paths (list): List of file paths to review.

        Returns:
            dict: Dictionary of reviews keyed by file path.
        """
        logger.info(f"🔍 [{self.role}] Reviewing files with GPT-4o...")

        with ThreadPoolExecutor() as executor:
            results = dict(executor.map(self._review_single_file, file_paths))

        logger.info("✅ Code review complete.")
        return results

    def _review_single_file(self, path: str) -> tuple:
        """
        Handles a single file review.

        Args:
            path (str): The relative file path.

        Returns:
            tuple: (path, review_text)
        """
        full_path = os.path.join(self.config.PROJECTS_DIR, path)

        if not os.path.isfile(full_path):
            return path, "❌ Skipped (not a valid file)"

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()

            if not code.strip():
                return path, "❌ Skipped (empty file)"

            review = self._review_with_gpt4(path, code)
            self.memory.save(f"ReviewerAgent::review::{path}", review)
            return path, review

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"❌ File read/review failed for {path}: {e}\n{error_details}")
            return path, f"❌ File read error: {e}"

    def _review_with_gpt4(self, file_path: str, code: str) -> str:
        """
        Calls GPT-4o to perform a code review.

        Args:
            file_path (str): Name of the file for context.
            code (str): The full code content.

        Returns:
            str: GPT-4o’s feedback or an error message.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a meticulous software reviewer. Point out issues, suggest improvements, and offer best practices."
                    },
                    {
                        "role": "user",
                        "content": f"Please review the following code from {file_path}:\n\n```{code}```"
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            error_details = traceback.format_exc()
            logger.error(f"GPT-4o API Error for {file_path}: {e}\n{error_details}")
            return "❌ GPT-4o Review Error: Retry later."
