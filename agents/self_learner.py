# self_learner.py
import os
import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SelfLearningAgent(BaseAgent):
    """Agent that studies logs and suggests improvements."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "SelfLearner"
        self.description = "Analyzes logs and proposes upgrades"

    def generate_plan(self, user_prompt: str):
        return {}

    def analyze_logs(self, log_path: str) -> str:
        if not os.path.isfile(log_path):
            return "No logs found"
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                data = f.read()[-2000:]
            prompt = (
                "Summarize recurring issues and suggest improvements for this log:\n"
                + data
            )
            suggestions = self.call_llm(prompt, model=self.config.GPT4_MODEL)
        except Exception as e:
            logger.error(f"Self-learning failed: {e}")
            suggestions = "Self-learning error"
        self.memory.save("SelfLearningAgent::last_suggestions", suggestions)
        return suggestions
