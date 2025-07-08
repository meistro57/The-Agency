"""Simple blueprint annotation utility."""
import re


def annotate_blueprint(text: str) -> str:
    """Return text with numbered annotations."""
    lines = text.splitlines()
    annotated = []
    for i, line in enumerate(lines, 1):
        if line.strip():
            annotated.append(f"[{i}] {line}")
        else:
            annotated.append(line)
    return "\n".join(annotated)
