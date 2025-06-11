# main.py

import logging
import signal
import sys
from config import Config
from agents.memory import MemoryManager
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.reviewer import ReviewerAgent
from agents.fixer import FixerAgent
from agents.deployer import DeployerAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Graceful exit handler
def handle_interrupt(sig, frame):
    logger.warning("\n🛑 Process interrupted. Shutting down gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)


def run_agency(prompt: str) -> None:
    """
    Orchestrates the Agency's full software lifecycle from idea to deployment.

    Args:
        prompt (str): User-defined project request.
    """
    if not prompt.strip():
        logger.error("🛑 Prompt cannot be empty.")
        return

    try:
        memory = MemoryManager()
        if not hasattr(Config, "GPT4_API_KEY") or not hasattr(Config, "OLLAMA_API_URL"):
            logger.error("🛑 Config is invalid. Please check required keys.")
            return

        logger.info("📡 Launching The Agency...")

        # Initialize agents
        architect = ArchitectAgent(Config, memory)
        coder     = CoderAgent(Config, memory)
        tester    = TesterAgent(Config, memory)
        reviewer  = ReviewerAgent(Config, memory)
        fixer     = FixerAgent(Config, memory)
        deployer  = DeployerAgent(Config, memory)

        # PLAN
        try:
            plan = architect.generate_plan(prompt)
            if not plan:
                logger.error("🛑 Architecture planning failed.")
                return
        except Exception as e:
            logger.exception(f"🛑 Error during planning: {e}")
            return

        # CODE
        try:
            code_files = coder.execute_plan(plan)
            if not code_files:
                logger.error("🛑 Code generation failed or no files were defined.")
                return
        except Exception as e:
            logger.exception(f"🛑 Error during code generation: {e}")
            return

        # TEST
        try:
            test_results = tester.run_tests(code_files)
        except Exception as e:
            logger.exception(f"🛑 Error during testing: {e}")
            test_results = {}

        # FIX (optional based on test results)
        if any(r.get("status") == "failed" for r in test_results.values() if isinstance(r, dict)):
            logger.info("🔧 Detected test failures — attempting fixes...")
            fixer.fix_code(code_files, test_results)

        # REVIEW
        try:
            reviewer.review_code(code_files)
        except Exception as e:
            logger.exception(f"🛑 Error during code review: {e}")

        # DEPLOY (prompt user to confirm)
        confirm = input("⚠️ Deploy the generated system? (yes/no): ").strip().lower()
        if confirm != "yes":
            logger.warning("🚫 Deployment cancelled.")
            return

        try:
            deployer.deploy_project(code_files)
        except Exception as e:
            logger.exception(f"🛑 Error during deployment: {e}")
            return

        logger.info("✅ All systems go.")

    except Exception as e:
        logger.exception(f"🔥 Unexpected failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        user_prompt = input("📝 What would you like The Agency to build today?\n> ")
        run_agency(user_prompt)
    except Exception as e:
        logger.exception(f"🧨 Fatal error at launch: {e}")
