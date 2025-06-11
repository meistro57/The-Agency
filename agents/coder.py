# coder.py

import os
import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LANGUAGE_MAP = {
    ".js": "JavaScript",
    ".py": "Python",
    ".html": "HTML",
    ".sql": "SQL",
    ".java": "Java",
}

FALLBACK_TEMPLATES = {
    ".js": lambda desc: f"// {desc}\n\nexport function placeholder() {{\n  console.log('TODO: Implement {desc}');\n}}",
    ".py": lambda desc: f"# {desc}\n\nif __name__ == '__main__':\n    print('TODO: Implement {desc}')",
    ".html": lambda desc: f"<!-- {desc} -->\n<!DOCTYPE html>\n<html>\n<head>\n  <title>{desc}</title>\n</head>\n<body>\n  <h1>{desc}</h1>\n</body>\n</html>",
    ".sql": lambda desc: f"-- {desc}\n-- TODO: Define SQL schema or query here",
}


class CoderAgent(BaseAgent):
    """
    Generates complete code files based on planning descriptions.
    """

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Code Generator"
        self.description = "Writes complete source files from planning specs"

    def generate_plan(self, user_prompt: str):
        return {}

    def execute_plan(self, plan: dict) -> list:
        logger.info(f"🛠️ [{self.role}] Generating code modules...")

        if not isinstance(plan, dict) or "files" not in plan:
            logger.error("Invalid plan format: missing 'files' key.")
            return []

        file_paths = []

        for spec in plan.get("files", []):
            path = os.path.normpath(spec.get("path", "").strip())
            description = spec.get("description", "No description provided").strip()

            if not path or path.endswith("/") or os.path.basename(path) == "":
                logger.info(f"📁 Skipping directory path: {path}")
                continue

            if ".." in path or path.startswith("/"):
                logger.error(f"❌ Skipping insecure or invalid path: {path}")
                continue

            try:
                code = self._generate_code(description, path)
                self._write_file(path, code)
                file_paths.append(path)
            except Exception as e:
                logger.error(f"❌ Failed to generate/write {path}: {e}")

        logger.info(f"✅ Code generation complete. Files: {file_paths}")
        return file_paths

    def _generate_code(self, description: str, path: str) -> str:
        """
        Uses LLM to generate code. Falls back if model fails.
        """
        language = self._infer_language(path)
        if len(description) > 500:
            description = description[:500] + "..."

        prompt = f"""
        Write a complete and functional {language} file for the following requirement:

        \"\"\"{description}\"\"\"

        The file should be ready to use and follow best practices.
        """

        try:
            code = self.call_llm(prompt, model=self.config.CODE_MODEL)
            return code.strip()
        except Exception as e:
            logger.warning(f"⚠️ Fallback for {path} due to LLM error: {e}")
            return self._fallback_code(description, path)

    def _write_file(self, path: str, code: str):
        """
        Writes the generated code to the filesystem.
        """
        abs_path = os.path.join(self.config.PROJECTS_DIR, path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(code)

    def _infer_language(self, path: str) -> str:
        ext = os.path.splitext(path)[1]
        return LANGUAGE_MAP.get(ext, "code")

    def _fallback_code(self, description: str, path: str) -> str:
        ext = os.path.splitext(path)[1]
        generator = FALLBACK_TEMPLATES.get(ext, lambda d: f"// {d}\n// TODO: Implement this file")
        return generator(description)
