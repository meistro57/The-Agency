import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RLOptimizer(BaseAgent):
    """Simple Q-learning optimizer for agent actions."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "RLOptimizer"
        self.description = "Learns optimal actions from rewards"
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.9

    def generate_plan(self, user_prompt: str):
        return {}

    def update(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value for a state-action pair."""
        self.q_table.setdefault(state, {}).setdefault(action, 0.0)
        next_max = max(self.q_table.get(next_state, {}).values(), default=0.0)
        old = self.q_table[state][action]
        self.q_table[state][action] = old + self.alpha * (
            reward + self.gamma * next_max - old
        )

    def select_action(self, state: str, actions: list[str]):
        """Choose the best known action for a state."""
        q_vals = self.q_table.get(state, {})
        if not q_vals:
            return actions[0]
        return max(actions, key=lambda a: q_vals.get(a, 0.0))
