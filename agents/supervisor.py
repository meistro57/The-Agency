import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SupervisorAgent(BaseAgent):
    """Validates agent outputs and ensures sanity of results."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Supervisor"
        self.description = "Checks outputs for basic errors"

    def generate_plan(self, user_prompt: str):
        return {}

    def validate_output(self, text: str) -> bool:
        if not text:
            return False
        lowered = text.lower()
        disallowed = ["traceback", "error:"]
        for pat in disallowed:
            if pat in lowered:
                logger.warning(f"Supervisor flagged output: {pat}")
                return False
        return True
