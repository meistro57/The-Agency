import os
import sys
import io
import tempfile
import subprocess
import importlib

import pytest

from agents.deployer import DeployerAgent
from agents.memory import MemoryManager
from interfaces import cli_interface
from interfaces.node_editor import app as node_app, NODES
from tools.refactor import suggest_refactors

class DummyConfig:
    GPT4_API_KEY = "k"
    OLLAMA_API_URL = "http://localhost"
    PROJECTS_DIR = tempfile.mkdtemp()
    CONTAINER_TOOL = "docker"

def test_refactor_suggestions(tmp_path):
    code = 'def f():\n    pass\n'
    fpath = tmp_path / 'a.py'
    fpath.write_text(code)
    report = suggest_refactors(str(fpath))
    assert 'Complexity' in report and 'Maintainability' in report


def test_cli_list_projects(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(cli_interface.Config, 'PROJECTS_DIR', str(tmp_path))
    (tmp_path / 'proj1').mkdir()
    sys.argv = ['cli', 'list-projects']
    cli_interface.main()
    out = capsys.readouterr().out
    assert 'proj1' in out


def test_cli_refactor_command(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(cli_interface.Config, 'PROJECTS_DIR', str(tmp_path))
    code = 'def f():\n    pass\n'
    file = tmp_path / 'file.py'
    file.write_text(code)
    sys.argv = ['cli', 'refactor', str(file)]
    cli_interface.main()
    out = capsys.readouterr().out
    assert 'Complexity' in out


def test_deployer_uses_podman(monkeypatch, tmp_path):
    DummyConfig.PROJECTS_DIR = str(tmp_path)
    DummyConfig.CONTAINER_TOOL = 'podman'
    agent = DeployerAgent(DummyConfig, MemoryManager())
    cmds = []
    monkeypatch.setattr(subprocess, 'run', lambda c, cwd=None, check=False: cmds.append(c))
    agent._build_docker_image('img')
    assert cmds and cmds[0][0] == 'podman'


def test_node_editor_post():
    client = node_app.test_client()
    resp = client.post('/', data={'name':'n1','text':'t'})
    assert resp.status_code == 200
    assert 'n1' in resp.get_data(as_text=True)

def test_setup_github_workflow(tmp_path):
    DummyConfig.PROJECTS_DIR = str(tmp_path)
    agent = DeployerAgent(DummyConfig, MemoryManager())
    agent.setup_github_workflow()
    wf = tmp_path / '.github' / 'workflows' / 'ci.yml'
    assert wf.exists()

