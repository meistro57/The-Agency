# failsafe.py
import logging
import re
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FailsafeAgent(BaseAgent):
    """Simple safety agent that scans text output for dangerous patterns."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "Failsafe"
        self.description = "Blocks dangerous or unethical output"
        self.patterns = [
            r"rm -rf",
            r"shutdown",
            r"drop table",
            r"delete from",
        ]

    def generate_plan(self, user_prompt: str):
        return {}

    def check_text(self, text: str) -> bool:
        """Return True if text is safe, False otherwise."""
        lowered = text.lower()
        for pat in self.patterns:
            if re.search(pat, lowered):
                logger.warning(f"🚨 Failsafe triggered by pattern: {pat}")
                self.memory.save("FailsafeAgent::alert", text)
                return False
        return True
