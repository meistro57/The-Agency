# coder.py

from agents.agent_base import BaseAgent
import os

class CoderAgent(BaseAgent):
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Code Generator"
        self.description = "Creates code files from the architecture plan"

    def generate_plan(self, user_prompt: str):
        # Satisfy abstract class contract
        return {}

    def execute_plan(self, plan: dict) -> list:
        print(f"\n🛠️ [{self.role}] Generating code modules...")
        files = plan.get("files", [])
        if not files:
            print("⚠️ No files defined in plan.")
            return []

        file_paths = []
        for spec in files:
            path = spec.get("path", "").strip()
            desc = spec.get("description", "No description provided").strip()

            # Skip empty or folder-only paths
            if not path or path.endswith("/") or os.path.basename(path) == "":
                print(f"📁 Skipping directory path: {path}")
                continue

            file_paths.append(path)
            code = self._generate_code(desc, path)
            self._write_file(path, code)

        print(f"✅ Code generation complete. Files: {file_paths}")
        return file_paths

    def _generate_code(self, description: str, path: str) -> str:
        prompt = f"""
Write a complete and functional {self._infer_language(path)} file for the following requirement:

\"\"\"{description}\"\"\"

The file should be ready to use and follow best practices.
"""

        try:
            response = self.call_llm(
                prompt=prompt,
                model=self.config.OLLAMA_MODEL,
                system=f"You are a professional software developer generating code for {path}."
            )

            if "TODO" in response or len(response.strip()) < 10:
                raise ValueError("LLM response looks like a placeholder or empty.")

            return response
        except Exception as e:
            print(f"⚠️ Failed to generate {path} from LLM. Falling back to basic stub. Reason: {e}")
            return self._fallback_code(description, path)

    def _infer_language(self, path: str) -> str:
        if path.endswith(".js"):
            return "JavaScript"
        if path.endswith(".py"):
            return "Python"
        if path.endswith(".html"):
            return "HTML"
        if path.endswith(".sql"):
            return "SQL"
        return "code"

    def _fallback_code(self, description: str, path: str) -> str:
        if path.endswith(".js"):
            return f"// {description}\n\nfunction placeholder() {{\n  console.log('TODO: Implement {description}');\n}}"
        elif path.endswith(".html"):
            return f"<!-- {description} -->\n<html>\n  <body>\n    <h1>{description}</h1>\n  </body>\n</html>"
        elif path.endswith(".py"):
            return f"# {description}\n\ndef placeholder():\n    print('TODO: Implement {description}')"
        elif path.endswith(".sql"):
            return f"-- {description}\n-- TODO: Define SQL schema here"
        else:
            return f"// {description}\n// TODO: Implement this file"

    def _write_file(self, rel_path: str, content: str):
        abs_path = os.path.join(self.config.PROJECTS_DIR, rel_path)

        # Skip directory-only paths
        if os.path.isdir(abs_path) or rel_path.endswith("/") or os.path.basename(rel_path) == "":
            print(f"📁 Skipping directory path: {rel_path}")
            return

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.memory.save(f"generated::{rel_path}", content)
