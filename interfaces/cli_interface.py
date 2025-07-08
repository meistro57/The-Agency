# cli_interface.py

import logging
import os
import sys
import argparse
import shutil

# Ensure the project root is on the path when running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_agency
from config import Config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    filename="cli_interface.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def launch_cli(input_func=input, output_func=print):
    """Interactive menu for running and resuming projects."""
    output_func("🕶️  Welcome to The Agency Terminal Interface")
    output_func("Type your request like you're the boss. I'll handle the rest.")

    while True:
        output_func("\nSelect an option:")
        output_func("1) New project")
        output_func("2) Continue project")
        output_func("3) Quit")
        try:
            choice = input_func("> ").strip().lower()

            if choice in {"3", "q", "quit", "exit"}:
                output_func("👋 Shutting down The Agency CLI.")
                logging.info("CLI shutdown by user.")
                break

            if choice in {"1", "n", "new"}:
                prompt = input_func("📝 What would you like The Agency to build?\n> ").strip()
                if not prompt:
                    output_func("⚠️  Please enter a valid request.")
                    continue
                logging.info(f"User input: {prompt}")
                run_agency(prompt)
                continue

            if choice in {"2", "c", "continue"}:
                projects = os.listdir(Config.PROJECTS_DIR)
                if not projects:
                    output_func("No past projects found.")
                    continue
                for idx, name in enumerate(projects, 1):
                    output_func(f"{idx}) {name}")
                sel = input_func("Select project number: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(projects):
                    output_func("Invalid selection.")
                    continue
                project = projects[int(sel) - 1]
                Config.PROJECTS_DIR = os.path.join(Config.PROJECTS_DIR, project)
                prompt = input_func("📝 What would you like to do next?\n> ").strip()
                if not prompt:
                    output_func("⚠️  Please enter a valid request.")
                    continue
                logging.info(f"Continuing {project} with prompt: {prompt}")
                run_agency(prompt)
                continue

            output_func("Invalid option. Try again.")

        except KeyboardInterrupt:
            output_func("\n👋 Shutting down The Agency CLI.")
            logging.info("CLI shutdown by user.")
            break
        except EOFError:
            output_func("\n👋 No input detected. Exiting.")
            logging.info("CLI received EOF; exiting.")
            break
        except Exception as e:
            output_func(f"🔥 An unexpected error occurred: {e}")
            logging.exception("Unexpected exception in CLI loop.")


def main():
    parser = argparse.ArgumentParser(description="The Agency CLI")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a new project")
    gen.add_argument("prompt", nargs="+", help="Project prompt")

    sub.add_parser("list-projects", help="List existing projects")

    delp = sub.add_parser("delete-project", help="Delete a project")
    delp.add_argument("name")

    ref = sub.add_parser("refactor", help="Suggest refactors for code")
    ref.add_argument("path")

    args = parser.parse_args()

    if args.command == "generate":
        run_agency(" ".join(args.prompt))
    elif args.command == "list-projects":
        projects = os.listdir(Config.PROJECTS_DIR)
        for p in projects:
            print(p)
    elif args.command == "delete-project":
        target = os.path.join(Config.PROJECTS_DIR, args.name)
        shutil.rmtree(target, ignore_errors=True)
        print(f"Deleted {args.name}")
    elif args.command == "refactor":
        from tools.refactor import suggest_refactors
        print(suggest_refactors(args.path))
    else:
        launch_cli()


if __name__ == "__main__":
    main()
