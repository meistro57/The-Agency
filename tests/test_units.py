import os
import tempfile
from agents.memory import MemoryManager
from agents.coder import CoderAgent
from agents.agent_base import BaseAgent

class DummyConfig:
    GPT4_API_KEY = "test-key"
    OLLAMA_API_URL = "http://localhost"
    CODE_MODEL = "test-model"
    PROJECTS_DIR = tempfile.mkdtemp()


def test_memory_manager_basic():
    mem = MemoryManager()
    mem.save("alpha", "beta")
    assert mem.get("alpha") == "beta"
    assert mem.get("missing", "default") == "default"


class DummyAgent(BaseAgent):
    def generate_plan(self, user_prompt: str):
        return {}


def test_build_messages():
    agent = DummyAgent(DummyConfig, MemoryManager())
    msgs = agent._build_messages("hi", "system")
    assert msgs == [{"role": "system", "content": "system"}, {"role": "user", "content": "hi"}]


def test_infer_language():
    coder = CoderAgent(DummyConfig, MemoryManager())
    assert coder._infer_language("main.py") == "Python"
    assert coder._infer_language("index.xyz") == "code"


def test_fallback_code():
    coder = CoderAgent(DummyConfig, MemoryManager())
    py_code = coder._fallback_code("do something", "task.py")
    assert "do something" in py_code
    assert "TODO" in py_code
