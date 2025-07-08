import logging
import requests
import types

from main import check_api_connections

class DummyConfig:
    OLLAMA_API_URL = "http://localhost:12345"
    GPT4_API_URL = "http://localhost:12346"
    REQUEST_TIMEOUT = 0.1

def test_check_api_connections_failure(monkeypatch, caplog):
    def fail(url, timeout):
        raise requests.ConnectionError("fail")
    monkeypatch.setattr("main.requests.get", fail)
    with caplog.at_level(logging.ERROR):
        ok = check_api_connections(DummyConfig)
    assert not ok
    assert "Cannot reach" in caplog.text

def test_check_api_connections_success(monkeypatch, caplog):
    class Resp:
        status_code = 200
    monkeypatch.setattr("main.requests.get", lambda url, timeout: Resp())
    with caplog.at_level(logging.ERROR):
        ok = check_api_connections(DummyConfig)
    assert ok
    assert not caplog.records

