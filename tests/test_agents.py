import tempfile
import pytest

from agents.architect import ArchitectAgent
from agents.deployer import DeployerAgent
from agents.coder import CoderAgent
from agents.agent_base import BaseAgent
from agents.memory import MemoryManager
from agents.main_agent import MainAgent
from agents.supervisor import SupervisorAgent


class DummyConfig:
    GPT4_API_KEY = "test-key"
    OLLAMA_API_URL = "http://localhost"
    CODE_MODEL = "test-model"
    ANTHROPIC_API_KEY = "test"
    PROJECTS_DIR = tempfile.mkdtemp()
    CONTAINER_TOOL = "docker"


class DummyAgent(BaseAgent):
    def generate_plan(self, user_prompt: str):
        return {}


def test_architect_plan_with_fallback(monkeypatch):
    mem = MemoryManager()
    agent = ArchitectAgent(DummyConfig, mem)

    def fake_llm(prompt: str, model: str = "gpt-4o", system: str = ""):
        return '{"components": ["web"], "tech_stack": {"frontend": "React"}}'

    monkeypatch.setattr(agent, "call_llm", fake_llm)
    plan = agent.generate_plan("build a web app")

    assert plan["components"] == ["web"]
    assert plan["files"]  # fallback files injected
    assert mem.get("ArchitectAgent::plan") == plan


def test_safe_json_parse_invalid():
    agent = ArchitectAgent(DummyConfig, MemoryManager())
    with pytest.raises(ValueError):
        agent.safe_json_parse("not json")


def test_deployer_generates_python_dockerfile(tmp_path):
    DummyConfig.PROJECTS_DIR = str(tmp_path)
    agent = DeployerAgent(DummyConfig, MemoryManager())
    agent._generate_dockerfile(["main.py"])

    dockerfile = tmp_path / "Dockerfile"
    assert dockerfile.exists()
    content = dockerfile.read_text()
    assert "FROM python" in content
    assert "CMD [\"python\"" in content


def test_coder_generate_code_fallback(monkeypatch, tmp_path):
    DummyConfig.PROJECTS_DIR = str(tmp_path)
    coder = CoderAgent(DummyConfig, MemoryManager())

    def fail_call(prompt: str, model: str = "", system: str = ""):
        raise RuntimeError("llm failure")

    monkeypatch.setattr(coder, "call_llm", fail_call)
    code = coder._generate_code("do something", "script.py")
    assert "TODO" in code


def test_call_llm_routes(monkeypatch):
    agent = DummyAgent(DummyConfig, MemoryManager())
    called = {}

    def fake_openai(model, prompt, system=""):
        called["openai"] = True
        return "ok"

    def fake_ollama(model, prompt, system=""):
        called["ollama"] = True
        return "ok"

    def fake_anthropic(model, prompt, system=""):
        called["anthropic"] = True
        return "ok"

    monkeypatch.setattr(agent, "_call_openai_chat", fake_openai)
    monkeypatch.setattr(agent, "_call_ollama_chat", fake_ollama)
    monkeypatch.setattr(agent, "_call_anthropic_chat", fake_anthropic)

    agent.call_llm("hello", model="gpt-test")
    assert "openai" in called and "ollama" not in called

    called.clear()
    agent.call_llm("hi", model="other")
    assert "ollama" in called and "openai" not in called

    called.clear()
    agent.call_llm("hey", model="claude-3")
    assert "anthropic" in called


def test_supervisor_validation():
    sup = SupervisorAgent(DummyConfig, MemoryManager())
    assert not sup.validate_output("error: failure")
    assert sup.validate_output("all good")


def test_main_agent_pipeline(monkeypatch, tmp_path):
    DummyConfig.PROJECTS_DIR = str(tmp_path)
    mem = MemoryManager()
    agent = MainAgent(DummyConfig, mem)

    monkeypatch.setattr(agent.architect, "generate_plan", lambda p: {"files": [{"path": "app.py", "description": "x"}]})
    monkeypatch.setattr(agent.coder, "_generate_code", lambda d, p: "print('hi')")
    monkeypatch.setattr(agent.tester, "run_tests", lambda f: {"app.py": {"status": "passed"}})
    monkeypatch.setattr(agent.reviewer, "review_code", lambda f: {})
    monkeypatch.setattr(agent.deployer, "deploy_project", lambda f: True)
    monkeypatch.setattr(agent.failsafe, "check_text", lambda t: True)
    monkeypatch.setattr(agent.fixer, "fix_code", lambda f, r: None)

    result = agent.run_pipeline("test")
    assert result["status"] == "success"
    assert (tmp_path / "app.py").exists()
