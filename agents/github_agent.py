import logging
import requests
from agents.agent_base import BaseAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GithubAgent(BaseAgent):
    """Simple wrapper around GitHub's REST API."""

    def __init__(self, config, memory):
        super().__init__(config, memory)
        self.token = getattr(config, "GITHUB_TOKEN", "")
        self.base_url = getattr(config, "GITHUB_API_URL", "https://api.github.com")
        self.headers = {"Authorization": f"token {self.token}"} if self.token else {}

    def generate_plan(self, user_prompt: str):
        return {}

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("headers", self.headers)
        try:
            resp = requests.request(method, url, **kwargs)
            if resp.ok:
                return resp.json()
            logger.error(f"GitHub API error {resp.status_code}: {resp.text}")
        except Exception as e:  # pragma: no cover - network dependent
            logger.error(f"GitHub request failed: {e}")
        return None

    def list_repos(self):
        data = self._request("GET", "/user/repos")
        if isinstance(data, list):
            return [r.get("name") for r in data]
        return []

    def create_repo(self, name: str, private: bool = False):
        payload = {"name": name, "private": private}
        return self._request("POST", "/user/repos", json=payload)

    def create_issue(self, repo: str, title: str, body: str = ""):
        payload = {"title": title, "body": body}
        return self._request("POST", f"/repos/{repo}/issues", json=payload)
