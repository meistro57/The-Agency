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


def test_semantic_search():
    mem = MemoryManager()
    mem.save("alpha", "make coffee")
    mem.save("beta", "make tea")
    results = mem.semantic_search("coffee")
    assert results and results[0] == "alpha"


def test_failsafe_detection():
    from agents.failsafe import FailsafeAgent
    fs = FailsafeAgent(DummyConfig, MemoryManager())
    assert not fs.check_text("run rm -rf now")
    assert not fs.check_text("sudo reboot")
    assert fs.check_text("hello world")


def test_blueprint_annotation():
    from tools.blueprint_annotator import annotate_blueprint
    text = "line1\nline2"
    annotated = annotate_blueprint(text)
    assert "[1] line1" in annotated


def test_product_creator_basic(monkeypatch):
    from agents.product_creator import ProductCreatorAgent
    agent = ProductCreatorAgent(DummyConfig, MemoryManager())
    monkeypatch.setattr(agent, "call_llm", lambda p, model="": '{"title": "t"}')
    spec = agent.generate_plan("t")
    assert spec["title"] == "t"


def test_rl_optimizer_update():
    from agents.rl_optimizer import RLOptimizer
    rl = RLOptimizer(DummyConfig, MemoryManager())
    rl.update("s1", "a1", 1.0, "s2")
    rl.update("s1", "a1", 1.0, "s2")
    assert rl.select_action("s1", ["a1", "a2"]) == "a1"
