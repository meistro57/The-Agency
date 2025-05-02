# context_loader.py

import os
import logging
import ast
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ContextLoader:
    """
    Loads source code files and extracts useful information for agent context prompts.
    """

    def __init__(self, config, memory):
        """
        Initialize the context loader.

        Args:
            config: Configuration object with PROJECTS_DIR path.
            memory: Optional memory store (not used in current version).
        """
        self.config = config
        self.memory = memory

    def load_code_snippets(self, file_paths: List[str]) -> Dict[str, Optional[str]]:
        """
        Reads the contents of each file path, storing as dictionary entries.

        Args:
            file_paths (List[str]): List of relative file paths under config.PROJECTS_DIR.

        Returns:
            Dict[str, str | None]: Mapping of file path to contents, or None if unreadable.
        """
        context = {}

        for path in file_paths:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)

            if not os.path.isfile(full_path):
                logger.warning(f"⚠️ Skipped (not a file): {path}")
                context[path] = None
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    context[path] = f.read()
            except FileNotFoundError:
                logger.warning(f"❌ File not found: {path}")
                context[path] = None
            except Exception as e:
                logger.error(f"❌ Error loading {path}: {e}")
                context[path] = None

        return context

    def extract_definitions(self, code: str) -> List[str]:
        """
        Uses AST parsing to extract function and class names from Python code.

        Args:
            code (str): Python source code.

        Returns:
            List[str]: Names of all top-level functions and classes.
        """
        try:
            tree = ast.parse(code)
            return [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
        except SyntaxError as e:
            logger.error(f"❌ Failed to parse code: {e}")
            return []