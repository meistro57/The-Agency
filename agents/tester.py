# tester.py

import os
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor
from agents.agent_base import BaseAgent

class TesterAgent(BaseAgent):
    """
    TesterAgent is responsible for executing Python files to detect runtime errors.
    It supports concurrent test execution and logs all results.

    Attributes:
        role (str): Role name used in logs and memory keys.
        description (str): Short description of the agent.
        logger (logging.Logger): Scoped logger for test output.
    """
    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Test Runner"
        self.description = "Executes Python files to detect runtime errors"
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def generate_plan(self, user_prompt: str):
        """Stub method required by BaseAgent abstract contract."""
        return {}

    def run_tests(self, file_paths: list) -> dict:
        """
        Run tests on a list of Python files and return structured results.

        Args:
            file_paths (list): List of string paths to Python files.

        Returns:
            dict: A dictionary of test results keyed by file path.
        """
        if not isinstance(file_paths, list) or not all(isinstance(p, str) for p in file_paths):
            raise ValueError("file_paths must be a list of strings")

        self.logger.info(f"🧪 [{self.role}] Running tests on generated files...")

        with ThreadPoolExecutor() as executor:
            results = dict(executor.map(self._run_single_test, file_paths))

        self.logger.info("✅ Testing complete.")
        return results

    def _run_single_test(self, path: str) -> tuple:
        """
        Run a test for a single Python file and return its result.

        Args:
            path (str): Relative path to the Python file.

        Returns:
            tuple: (path, result_dict)
        """
        full_path = os.path.join(self.config.PROJECTS_DIR, path)

        if not full_path.endswith(".py") or not os.path.isfile(full_path):
            return path, {"status": "skipped", "message": "Not a Python file"}

        if not full_path.startswith(self.config.PROJECTS_DIR):
            return path, {"status": "failed", "message": f"Unsafe path: {full_path}"}

        try:
            timeout = getattr(self.config, "TEST_TIMEOUT", 10)
            output = subprocess.check_output(
                ["python3", full_path],
                stderr=subprocess.STDOUT,
                timeout=timeout
            )
            result = {"status": "passed", "message": output.decode()}
        except subprocess.CalledProcessError as e:
            result = {"status": "failed", "message": f"Runtime error:\n{e.output.decode()}"}
        except subprocess.TimeoutExpired:
            result = {"status": "failed", "message": "Timed out"}
        except Exception as e:
            result = {"status": "failed", "message": f"Unexpected error: {str(e)}"}

        self.memory.save(f"TesterAgent::test_result::{path}", result)
        return path, result
