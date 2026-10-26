"""Configuration: the example is valid and an invalid value fails with a clear message."""

import codecs
import tomllib
from datetime import date
from pathlib import Path

import pytest

from job_search_agent.config import PROJECT_ROOT, ConfigError, load_config, parse_config

EXAMPLE = PROJECT_ROOT / "config.example.toml"


@pytest.fixture
def data(tmp_path: Path) -> dict:
    """The example configuration with a real absolute path for the server database."""
    parsed = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))
    parsed["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    return parsed


def test_example_is_valid(data: dict, tmp_path: Path) -> None:
    config = parse_config(data, root=tmp_path)
    assert config.models == {
        "router": "gpt-6-luna",
        "agent": "gpt-6.1-sol",
        "embeddings": "text-embedding-3-small",
    }
    assert config.pricing["gpt-6.1-sol"].output == 10.0
    assert config.pricing["text-embedding-3-small"].output is None
    assert config.limits.recursion_limit == 12
    assert config.checkpoints == tmp_path / "data" / "local" / "checkpoints.db"
    assert config.reference_date == date(2026, 3, 16)
    assert "Ana Exemplo" in config.masking_names


def test_server_env_has_only_server_variables(data: dict) -> None:
    data["server"]["JOB_SEARCH_CONFIG"] = str(
        Path(data["server"]["JOB_SEARCH_DB"]).parent / "s.toml"
    )
    env = parse_config(data).server.env()
    assert set(env) == {"JOB_SEARCH_DB", "JOB_SEARCH_CONFIG"}


def test_missing_price_is_refused(data: dict) -> None:
    del data["pricing"]["gpt-6.1-sol"]
    with pytest.raises(ConfigError, match=r"no price for model 'gpt-6.1-sol'"):
        parse_config(data)


def test_missing_output_price_is_refused(data: dict) -> None:
    del data["pricing"]["gpt-6-luna"]["output"]
    with pytest.raises(ConfigError, match=r'\[pricing."gpt-6-luna"\] output'):
        parse_config(data)


@pytest.mark.parametrize("value", [0, -1, True, "12", 1.5])
def test_invalid_limit_is_refused(data: dict, value) -> None:
    data["limits"]["recursion_limit"] = value
    with pytest.raises(ConfigError, match=r"\[limits\] recursion_limit must be a positive integer"):
        parse_config(data)


def test_turn_limit_above_day_limit_is_refused(data: dict) -> None:
    data["limits"]["max_tokens_per_turn"] = data["limits"]["max_tokens_per_day"] + 1
    with pytest.raises(ConfigError, match="max_tokens_per_turn"):
        parse_config(data)


@pytest.mark.parametrize("key", ["JOB_SEARCH_DB", "JOB_SEARCH_CONFIG"])
def test_relative_server_path_is_refused(data: dict, key: str) -> None:
    data["server"][key] = "data/local/job_search.db"
    with pytest.raises(ConfigError, match=rf"\[server\] {key} must be an absolute path"):
        parse_config(data)


def test_missing_section_is_refused(data: dict) -> None:
    del data["limits"]
    with pytest.raises(ConfigError, match=r"missing section \[limits\]"):
        parse_config(data)


def test_invalid_reference_date_is_refused(data: dict) -> None:
    data["demo"]["reference_date"] = "16/03/2026"
    with pytest.raises(ConfigError, match="reference_date"):
        parse_config(data)


def test_missing_file_explains_what_to_do(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="Copy config.example.toml to config.toml"):
        load_config(tmp_path / "config.toml")


def test_invalid_toml_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("[models\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid TOML"):
        load_config(path)


def test_file_with_bom_is_read(tmp_path: Path) -> None:
    text = EXAMPLE.read_text(encoding="utf-8").replace(
        "C:/caminho/absoluto/para/job-search-agent/data/local/job_search.db",
        (tmp_path / "job_search.db").as_posix(),
    )
    path = tmp_path / "config.toml"
    path.write_text(text, encoding="utf-8-sig")
    assert path.read_bytes().startswith(codecs.BOM_UTF8)
    assert load_config(path).server.db == tmp_path / "job_search.db"
