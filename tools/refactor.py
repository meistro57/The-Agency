import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _run_radon(args: List[str]) -> str:
    try:
        result = subprocess.run(["radon", *args], capture_output=True, text=True)
        return result.stdout or result.stderr
    except FileNotFoundError:
        return "radon command not found. Please install with 'pip install radon'."
    except Exception as e:
        logger.error(f"Failed to run radon: {e}")
        return str(e)

def suggest_refactors(path: str) -> str:
    """Return simple refactoring suggestions using radon metrics."""
    complexity = _run_radon(["cc", "-s", path])
    maintain = _run_radon(["mi", "-s", path])
    suggestions = []
    if "F" in complexity or "F" in maintain:
        suggestions.append("High complexity detected. Consider simplifying functions.")
    if "D" in maintain:
        suggestions.append("Maintainability is low. Break up large modules or functions.")
    report = "--- Complexity ---\n" + complexity + "\n--- Maintainability ---\n" + maintain
    if suggestions:
        report += "\n--- Suggestions ---\n" + "\n".join(suggestions)
    return report
