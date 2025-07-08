import os
import logging
from agents.agent_base import BaseAgent
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from agents.reviewer import ReviewerAgent
from agents.fixer import FixerAgent
from agents.deployer import DeployerAgent
from agents.failsafe import FailsafeAgent
from agents.task_manager import TaskManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MainAgent(BaseAgent):
    """Central coordinator that runs the full code generation pipeline."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "MainAgent"
        self.description = "Coordinates all other agents"
        self.task_manager = TaskManager()
        self.architect = ArchitectAgent(config, memory)
        self.coder = CoderAgent(config, memory)
        self.tester = TesterAgent(config, memory)
        self.reviewer = ReviewerAgent(config, memory)
        self.fixer = FixerAgent(config, memory)
        self.deployer = DeployerAgent(config, memory)
        self.failsafe = FailsafeAgent(config, memory)
        self.supervisor = None

    def generate_plan(self, user_prompt: str):
        return self.run_pipeline(user_prompt)

    def run_pipeline(self, user_prompt: str) -> dict:
        plan = self.architect.generate_plan(user_prompt)
        if not plan:
            return {"status": "failed", "reason": "planning_error"}

        code_files = self.coder.execute_plan(plan)
        if not code_files:
            return {"status": "failed", "reason": "code_gen_error"}

        # failsafe scan
        for path in code_files:
            full_path = os.path.join(self.config.PROJECTS_DIR, path)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    if not self.failsafe.check_text(f.read()):
                        return {"status": "failed", "reason": "failsafe"}
            except FileNotFoundError:
                continue

        results = self.tester.run_tests(code_files)
        if any(r.get("status") == "failed" for r in results.values() if isinstance(r, dict)):
            self.fixer.fix_code(code_files, results)

        self.reviewer.review_code(code_files)
        self.deployer.deploy_project(code_files)
        return {"status": "success", "files": code_files, "tests": results}
