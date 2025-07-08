# main.py

import logging
import signal
import sys
import os
import importlib
import pkgutil
from config import Config
from agents.memory import MemoryManager
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.reviewer import ReviewerAgent
from agents.fixer import FixerAgent
from agents.deployer import DeployerAgent
from agents.failsafe import FailsafeAgent
from agents.evolution_logger import EvolutionLogger
from agents.self_learner import SelfLearningAgent
from agents.product_creator import ProductCreatorAgent
from agents.rl_optimizer import RLOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Graceful exit handler
def handle_interrupt(sig, frame):
    logger.warning("\n🛑 Process interrupted. Shutting down gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)


def load_extension_agents(config, memory):
    """Dynamically load agents from agents/extensions directory."""
    agents = []
    ext_dir = os.path.join(os.path.dirname(__file__), "agents", "extensions")
    if not os.path.isdir(ext_dir):
        return agents

    for _, module_name, _ in pkgutil.iter_modules([ext_dir]):
        full_name = f"agents.extensions.{module_name}"
        try:
            module = importlib.import_module(full_name)
            if hasattr(module, "Agent"):
                agent_cls = getattr(module, "Agent")
                agents.append(agent_cls(config, memory))
                logger.info(f"🔌 Loaded extension agent {agent_cls.__name__}")
        except Exception as e:
            logger.error(f"❌ Failed to load extension agent {module_name}: {e}")

    return agents


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
        failsafe  = FailsafeAgent(Config, memory)
        evo_log   = EvolutionLogger(Config, memory)
        learner   = SelfLearningAgent(Config, memory)
        producter = ProductCreatorAgent(Config, memory)
        optimizer = RLOptimizer(Config, memory)
        extra_agents = load_extension_agents(Config, memory)
        if extra_agents:
            logger.info(f"🔄 Loaded {len(extra_agents)} extension agents.")

        # PLAN
        try:
            plan = architect.generate_plan(prompt)
            if not plan:
                logger.error("🛑 Architecture planning failed.")
                return
        except Exception as e:
            logger.exception(f"🛑 Error during planning: {e}")
            return
        evo_log.log_event("planning_complete")

        # CODE
        try:
            code_files = coder.execute_plan(plan)
            if not code_files:
                logger.error("🛑 Code generation failed or no files were defined.")
                return
        except Exception as e:
            logger.exception(f"🛑 Error during code generation: {e}")
            return
        for path in code_files:
            full_path = os.path.join(Config.PROJECTS_DIR, path)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    if not failsafe.check_text(f.read()):
                        logger.error("🛑 Failsafe triggered. Aborting.")
                        return
            except FileNotFoundError:
                continue
        evo_log.log_event("code_generated")

        # TEST
        try:
            test_results = tester.run_tests(code_files)
        except Exception as e:
            logger.exception(f"🛑 Error during testing: {e}")
            test_results = {}
        evo_log.log_event("tests_run")

        # FIX (optional based on test results)
        if any(r.get("status") == "failed" for r in test_results.values() if isinstance(r, dict)):
            logger.info("🔧 Detected test failures — attempting fixes...")
            fixer.fix_code(code_files, test_results)
            evo_log.log_event("fixes_applied")

        # REVIEW
        try:
            reviewer.review_code(code_files)
        except Exception as e:
            logger.exception(f"🛑 Error during code review: {e}")
        evo_log.log_event("review_complete")

        # DEPLOY (prompt user to confirm)
        confirm = input("⚠️ Deploy the generated system? (yes/no): ").strip().lower()
        if confirm != "yes":
            logger.warning("🚫 Deployment cancelled.")
            return

        try:
            deployer.deploy_project(code_files)
            spec = producter.generate_plan(prompt)
            producter.upload_product(spec)
            optimizer.update("pipeline", "deploy", 1.0, "done")
        except Exception as e:
            logger.exception(f"🛑 Error during deployment: {e}")
            return
        evo_log.log_event("deployed")

        learner.analyze_logs(os.path.join(Config.LOGS_DIR, "agency.log"))
        
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
