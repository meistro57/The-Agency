import os
import types
import io
import tempfile
import subprocess
from agents.deployer import DeployerAgent
from agents.marketplace import AgentMarketplace
from agents.extensions.manager import ExtensionManager
from tools.retriever import SimpleRetriever
from interfaces.web_dashboard import app
from agents.memory import MemoryManager

class DummyConfig:
    GPT4_API_KEY = "k"
    OLLAMA_API_URL = "http://localhost"
    PROJECTS_DIR = tempfile.mkdtemp()


def test_extension_manager_load(tmp_path, monkeypatch):
    ext_dir = tmp_path / "ext"
    ext_dir.mkdir()
    (ext_dir / "mod.py").write_text("def register(m): m.register('x','y')")
    ExtensionManager.REGISTRY.clear()
    ExtensionManager.load_extensions(str(ext_dir))
    assert ExtensionManager.get('x') == 'y'


def test_marketplace_register_and_create():
    class DummyAgent:
        def __init__(self, c, m):
            self.cfg = c
    mp = AgentMarketplace()
    mp.register_agent('dummy', DummyAgent)
    assert 'dummy' in mp.list_agents()
    agent = mp.create_agent('dummy', None, None)
    assert isinstance(agent, DummyAgent)


def test_deployer_auto_push(monkeypatch):
    calls = []
    def fake_run(cmd, cwd=None, check=False):
        calls.append(cmd)
    monkeypatch.setattr(subprocess, 'run', fake_run)
    dep = DeployerAgent(DummyConfig, MemoryManager())
    dep.auto_push_to_github('git@example.com:repo.git')
    assert any('git' in c[0] for c in calls)


def test_retriever_search(tmp_path):
    d = tmp_path
    f1 = d / 'a.txt'; f1.write_text('hello world')
    f2 = d / 'b.txt'; f2.write_text('another file')
    r = SimpleRetriever()
    r.index_folder(str(d))
    results = r.search('hello')
    assert results and str(f1) in results[0]


def test_dashboard_upload_route(tmp_path):
    client = app.test_client()
    data = {'file': (io.BytesIO(b'test prompt'), 'bp.txt')}
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 202
