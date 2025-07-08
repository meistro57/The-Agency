# evolution_logger.py
import os
from datetime import datetime
import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EvolutionLogger(BaseAgent):
    """Logs system evolution events for later analysis."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "EvolutionLogger"
        self.description = "Tracks improvements and changes over time"
        self.log_path = os.path.join(config.LOGS_DIR, "evolution.log")
        os.makedirs(config.LOGS_DIR, exist_ok=True)

    def generate_plan(self, user_prompt: str):
        return {}

    def log_event(self, message: str):
        ts = datetime.utcnow().isoformat()
        entry = f"{ts} - {message}"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        self.memory.save(f"Evolution::{ts}", message)
        logger.info(f"📈 Evolution logged: {message}")
