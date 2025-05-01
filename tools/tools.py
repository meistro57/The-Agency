# tools.py

import subprocess

def run_python_code(filepath: str) -> str:
    """Executes a Python file and returns stdout + stderr."""
    try:
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return "✅ Success\n" + result.stdout
        else:
            return f"❌ Error (code {result.returncode})\n{result.stderr}"
    except Exception as e:
        return f"🔥 Execution failed: {e}"

def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
