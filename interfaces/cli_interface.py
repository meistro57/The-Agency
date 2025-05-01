# cli_interface.py

from main import run_agency

def launch_cli():
    print("🕶️  Welcome to The Agency Terminal Interface")
    print("Type your request like you're the boss. I’ll handle the rest.")
    print("To exit, press Ctrl+C\n")

    while True:
        try:
            prompt = input("📝 What would you like The Agency to build?\n> ")
            run_agency(prompt)
        except KeyboardInterrupt:
            print("\n👋 Shutting down The Agency CLI.")
            break

if __name__ == "__main__":
    launch_cli()
