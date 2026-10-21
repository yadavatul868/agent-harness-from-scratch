import pytest

from agent_harness_from_scratch.model import DEFAULT_BASE_URL, make_client


def test_make_client_defaults_to_local_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)

    client = make_client()

    assert str(client.base_url) == f"{DEFAULT_BASE_URL}/"


def test_make_client_reads_endpoint_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_BASE_URL", "https://router.huggingface.co/v1")
    monkeypatch.setenv("MODEL_API_KEY", "test-key")

    client = make_client()

    assert str(client.base_url) == "https://router.huggingface.co/v1/"
    assert client.api_key == "test-key"
