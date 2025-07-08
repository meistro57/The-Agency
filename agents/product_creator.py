import json
import logging
import requests
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ProductCreatorAgent(BaseAgent):
    """Creates simple product listings and optionally uploads them."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.role = "ProductCreator"
        self.description = "Generates product specs and uploads via API"

    def generate_plan(self, user_prompt: str) -> dict:
        """Use the LLM to create a structured product specification."""
        prompt = (
            "You are a product generation assistant. "
            "Return a JSON object with title, description and tags for: "
            f"{user_prompt}"
        )
        try:
            text = self.call_llm(prompt, model=self.config.CODE_MODEL)
            spec = json.loads(text)
        except Exception:
            logger.warning("Fallback to basic spec due to LLM failure")
            spec = {"title": user_prompt, "description": user_prompt, "tags": []}
        self.memory.save("product_spec", spec)
        return spec

    def upload_product(self, spec: dict) -> bool:
        """Upload the product spec to the configured Printify endpoint."""
        url = getattr(self.config, "PRINTIFY_API_URL", "")
        token = getattr(self.config, "PRINTIFY_API_KEY", "")
        if not url or not token:
            logger.info("Printify configuration missing; skipping upload")
            return False
        try:
            headers = {"Authorization": f"Bearer {token}"}
            requests.post(url, json=spec, headers=headers, timeout=30)
            logger.info("✅ Uploaded product spec")
            return True
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return False
