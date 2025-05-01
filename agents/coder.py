# coder.py

from agents.agent_base import BaseAgent
import os

class CoderAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Code Generator"
        self.description = "Writes code files based on the architecture plan."

    def execute_plan(self, plan: dict) -> list:
        print(f"\n🛠️ [{self.role}] Generating code modules...")
        generated_files = []

        files = plan.get("files", [])
        if not files:
            print("⚠️ No files defined in plan.")
            return []

        for file_spec in files:
            path = file_spec.get("path", "unknown.py")
            desc = file_spec.get("description", "No description provided.")
            code = self._generate_code(path, desc)
            if code:
                self._save_file(path, code)
                generated_files.append(path)

        print(f"✅ Code generation complete. Files: {generated_files}")
        return generated_files

    def _generate_code(self, file_path: str, description: str) -> str:
        prompt = f"""
        You are a professional software engineer. Please generate the code for the following file:

        File Path: {file_path}
        Description: {description}

        Requirements:
        - Begin with a comment stating the filename
        - Make it production-quality
        - Match the project’s overall structure

        Return only the code content.
        """

        return self.call_llm(prompt, model="ollama", system="You are a senior developer.")

    def _save_file(self, path: str, code: str):
        full_path = os.path.join(self.config.PROJECTS_DIR, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(code)
