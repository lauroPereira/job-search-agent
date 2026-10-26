"""Provider interface, without network and without a real key."""

import tomllib
from pathlib import Path

import pytest

from job_search_agent import llm
from job_search_agent.config import PROJECT_ROOT, parse_config


@pytest.fixture
def config(tmp_path: Path):
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    return parse_config(data, root=tmp_path)


def test_chat_model_uses_responses_api(config, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    model = llm.chat_model("router", config)
    assert model.model_name == "gpt-6-luna"
    assert model.use_responses_api is True
    assert model.reasoning == {"effort": "low"}
    assert model.max_tokens == 2000


def test_unknown_role_is_refused(config) -> None:
    with pytest.raises(ValueError, match="Unknown model role"):
        llm.chat_model("writer", config)


def test_smoke_without_key_does_not_call(config, monkeypatch, capsys) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert llm.smoke(config) == 2
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().err
