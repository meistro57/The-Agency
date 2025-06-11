# tools.py

import os
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_python_code(filepath: str, timeout: int = 10) -> str:
    """
    Executes a Python script and returns stdout + stderr.

    Args:
        filepath (str): Path to the Python file.
        timeout (int): Max time to wait before killing the process.

    Returns:
        str: Execution result or error message.
    """
    try:
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return "✅ Success\n" + result.stdout
        else:
            return f"❌ Error (code {result.returncode})\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return f"🔥 Execution failed: Timeout after {timeout} seconds"
    except FileNotFoundError:
        return "🔥 Execution failed: Python interpreter not found"
    except Exception as e:
        logger.exception(f"Unexpected error running {filepath}: {e}")
        return f"🔥 Execution failed: {e}"


def write_file(path: str, content: str) -> bool:
    """
    Writes content to a file. Creates parent folders if needed.

    Args:
        path (str): File path.
        content (str): Text content to write.

    Returns:
        bool: True on success, False on error.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"🔥 Failed to write to {path}: {e}")
        return False


def read_file(path: str) -> str:
    """
    Reads text from a file.

    Args:
        path (str): File path.

    Returns:
        str: File contents or error message.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"🔥 File not found: {path}"
    except Exception as e:
        logger.error(f"🔥 Failed to read {path}: {e}")
        return f"🔥 Failed to read file: {e}"
