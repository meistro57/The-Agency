# context_loader.py

import os

class ContextLoader:
    def __init__(self, config):
        self.config = config

    def load_code_snippets(self, file_paths: list) -> dict:
        """Load contents of code files for context-aware prompts."""
        context = {}
        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    context[path] = f.read()
        return context

    def extract_definitions(self, code: str) -> list:
        """Extract function or class names from Python code (simple)."""
        import re
        matches = re.findall(r'^\s*(def|class)\s+(\w+)', code, re.MULTILINE)
        return [name for _, name in matches]
