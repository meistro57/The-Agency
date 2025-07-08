import os
import logging
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class InstructionsAgent(BaseAgent):
    """Creates basic README instructions for running the generated project."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "InstructionsAgent"
        self.description = "Writes usage instructions for the project"

    def generate_plan(self, user_prompt: str):
        return {}

    def write_readme(self, entry: str = "main.py") -> str:
        """Create README.md in the project directory with run instructions."""
        readme_path = os.path.join(self.config.PROJECTS_DIR, "README.md")
        content = f"""
# How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Execute the program:
```bash
python {entry}
```
"""
        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            self.memory.save("instructions_path", readme_path)
            logger.info("📝 Instructions README created.")
        except Exception as e:
            logger.error(f"❌ Failed to write README: {e}")
        return readme_path
