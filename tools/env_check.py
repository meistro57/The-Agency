"""Environment verification utility."""
import shutil
import sys


def check_python(min_major=3, min_minor=10) -> None:
    if sys.version_info < (min_major, min_minor):
        raise RuntimeError(f"Python {min_major}.{min_minor}+ required")


def check_docker() -> None:
    if not shutil.which("docker"):
        raise RuntimeError("Docker is not installed or not in PATH")


if __name__ == "__main__":
    try:
        check_python()
        check_docker()
    except Exception as e:
        print(f"Environment check failed: {e}")
    else:
        print("Environment looks good")
