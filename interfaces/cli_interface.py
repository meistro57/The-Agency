# cli_interface.py

import logging
import os
import sys

# Ensure the project root is on the path when running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_agency

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    filename="cli_interface.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def launch_cli(input_func=input, output_func=print):
    """
    Launches the CLI interface for The Agency.
    Accepts optional input/output functions for testability.
    """
    output_func("🕶️  Welcome to The Agency Terminal Interface")
    output_func("Type your request like you're the boss. I’ll handle the rest.")
    output_func("To exit, press Ctrl+C\n")

    while True:
        try:
            prompt = input_func("📝 What would you like The Agency to build?\n> ").strip()

            if not prompt:
                output_func("⚠️  Please enter a valid request.")
                continue

            if prompt.lower() in {"help", "?"}:
                output_func("ℹ️  Enter a plain-English request to build software.")
                output_func("    Example: A website to track planets using React + Flask.")
                output_func("    Press Ctrl+C to exit.\n")
                continue

            logging.info(f"User input: {prompt}")
            run_agency(prompt)

        except KeyboardInterrupt:
            output_func("\n👋 Shutting down The Agency CLI.")
            logging.info("CLI shutdown by user.")
            break

        except Exception as e:
            output_func(f"🔥 An unexpected error occurred: {e}")
            logging.exception("Unexpected exception in CLI loop.")


if __name__ == "__main__":
    launch_cli()