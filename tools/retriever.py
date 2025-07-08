import os
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SimpleRetriever:
    """Index and search text documents with basic similarity scoring."""

    def __init__(self):
        self.index = {}

    def index_folder(self, directory: str, exts=(".md", ".txt")) -> None:
        for root, _, files in os.walk(directory):
            for name in files:
                if name.endswith(exts):
                    path = os.path.join(root, name)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            self.index[path] = f.read().lower()
                    except Exception as e:
                        logger.error(f"Failed to read {path}: {e}")

    def search(self, query: str, top_k: int = 3):
        query = query.lower()
        scored = []
        for path, text in self.index.items():
            score = SequenceMatcher(None, query, text).ratio()
            scored.append((score, path))
        scored.sort(reverse=True)
        return [p for _, p in scored[:top_k]]
