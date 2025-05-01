# architect.py

import os
import re
import json
import traceback
import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ArchitectAgent(BaseAgent):
    """
    ArchitectAgent is responsible for generating a software architecture plan based on a user prompt.
    It uses an LLM to break the task into components, technologies, and required files.
    """

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "System Architect"
        self.description = "Decomposes user prompt into a software plan"

    def generate_plan(self, user_prompt: str) -> dict:
        """
        Generates a software architecture plan from the given user prompt.

        Args:
            user_prompt (str): The prompt describing what software to build.

        Returns:
            dict: A validated and normalized software plan dictionary.
        """
        logger.info(f"\n🧠 [{self.role}] Planning using GPT-4o...")

        planning_prompt = f"""
You are a senior software architect. A user has asked you to build the following:
\"\"\"{user_prompt}\"\"\"

Break this into a clear software architecture plan:
- List major components (frontend, backend, database, etc.)
- Recommend appropriate technologies and frameworks
- Define core files/modules and what they will do
- Include any setup notes or gotchas

Return ONLY valid JSON with:
- components: [list of system parts]
- tech_stack: dictionary of chosen tools per part
- files: list of {{ path, description }}
- notes: any important planning or security details
"""

        try:
            plan_response = self._generate_with_llm(planning_prompt)
            logger.debug("📝 Raw plan response:\n" + plan_response)
            plan = self.safe_json_parse(plan_response)
            plan = self.normalize_plan(plan)
        except Exception as e:
            logger.error(f"❌ Failed to parse architecture plan: {e}")
            return {}

        if not plan.get("files"):
            logger.warning("⚠️ Plan has no 'files'. Injecting fallback starter files...")
            plan["files"] = self._fallback_file_plan(user_prompt)

        self.memory.save(f"{self.__class__.__name__}::plan", plan)
        logger.info("✅ Plan successfully created and saved.")
        return plan

    def _generate_with_llm(self, prompt: str) -> str:
        """
        Wraps the LLM call using GPT-4o.

        Args:
            prompt (str): Prompt to send to the LLM.

        Returns:
            str: Raw JSON string response.
        """
        return self.call_llm(
            prompt=prompt,
            model="gpt-4o",
            system="You are a software architect responding only with structured JSON."
        )

    def safe_json_parse(self, raw_text: str) -> dict:
        """
        Attempts to safely parse JSON from raw LLM output, with Markdown and newline handling.

        Args:
            raw_text (str): The raw response text.

        Returns:
            dict: Parsed JSON as a dictionary.
        """
        if not raw_text:
            raise ValueError("Empty response from LLM")

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1).strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3].strip()

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass

        # Fallback regex to extract JSON blob
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as e:
                raise ValueError(f"Malformed JSON: {e}")

        raise ValueError("No JSON found in response")

    def normalize_plan(self, plan: dict) -> dict:
        """
        Ensures the 'files' field is formatted as a list of { path, description }.

        Args:
            plan (dict): The raw plan dictionary.

        Returns:
            dict: Normalized plan.
        """
        raw_files = plan.get("files")
        if isinstance(raw_files, dict):
            plan["files"] = [
                {"path": k.strip(), "description": v.strip()}
                for k, v in raw_files.items()
            ]
        elif isinstance(raw_files, list):
            plan["files"] = [
                f if isinstance(f, dict) and "path" in f
                else {"path": str(f), "description": "Auto-generated"}
                for f in raw_files
            ]
        else:
            plan["files"] = []

        return plan

    def _fallback_file_plan(self, user_prompt: str) -> list:
        """
        Returns a minimal viable file list based on generic expectations.

        Args:
            user_prompt (str): The original task, used to infer fallback needs.

        Returns:
            list: List of fallback file specs.
        """
        return [
            {
                "path": "frontend/upload_form.html",
                "description": "Basic form UI for uploading a file"
            },
            {
                "path": "backend/server.py",
                "description": "Flask or Express server for handling uploads and calling AI"
            },
            {
                "path": "templates/report.html",
                "description": "Template HTML for displaying a result"
            },
            {
                "path": "README.md",
                "description": f"Instructions and description of this tool: {user_prompt}"
            }
        ]
