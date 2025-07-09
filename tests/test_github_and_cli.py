import sys
import types

import requests

from agents.github_agent import GithubAgent
from agents.memory import MemoryManager
from interfaces import cli_interface

class DummyConfig:
    GPT4_API_KEY = 'k'
    OLLAMA_API_URL = 'http://localhost'
    GITHUB_API_URL = 'http://example.com'
    GITHUB_TOKEN = 't'
    PROJECTS_DIR = ''

def test_github_agent_list(monkeypatch):
    def fake_request(method, url, **kwargs):
        class Resp:
            ok = True
            def json(self):
                return [{'name': 'repo1'}]
        return Resp()
    monkeypatch.setattr(requests, 'request', fake_request)
    agent = GithubAgent(DummyConfig, MemoryManager())
    repos = agent.list_repos()
    assert 'repo1' in repos


def test_cli_continue_menu(tmp_path, monkeypatch):
    DummyConfig.PROJECTS_DIR = str(tmp_path)
    (tmp_path / 'proj1').mkdir()
    inputs = iter(['2', '1', 'do something', '3'])
    outputs = []
    cli_interface.Config.PROJECTS_DIR = str(tmp_path)
    cli_interface.launch_cli(input_func=lambda _: next(inputs), output_func=outputs.append)
    joined = '\n'.join(outputs)
    assert 'proj1' in joined
    assert 'Shutting down' in joined

