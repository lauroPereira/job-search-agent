"""Local configuration: config.toml (models, prices, limits, paths, server) and .env (API key).

Every key of config.example.toml is required, except server.JOB_SEARCH_CONFIG. A missing or
invalid value raises ConfigError with the section and key, so the app does not start with a
wrong price, limit or database path.
"""

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# Project root (the directory with pyproject.toml), so paths do not depend on the working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.toml"
ENV_PATH = PROJECT_ROOT / ".env"

CHAT_ROLES = ("router", "agent")


class ConfigError(Exception):
    """config.toml is missing or has a missing or invalid value."""


@dataclass(frozen=True)
class Price:
    """US$ per 1 million tokens. Embedding models only have `input`."""

    input: float
    cached_input: float | None = None
    output: float | None = None


@dataclass(frozen=True)
class Limits:
    max_tokens_per_turn: int
    max_tokens_per_day: int
    recursion_limit: int
    max_output_tokens: int


@dataclass(frozen=True)
class Server:
    command: str
    db: Path
    config: Path | None = None

    def env(self) -> dict[str, str]:
        """Variables passed to the server process (and nothing else: no API key)."""
        env = {"JOB_SEARCH_DB": str(self.db)}
        if self.config is not None:
            env["JOB_SEARCH_CONFIG"] = str(self.config)
        return env


@dataclass(frozen=True)
class Config:
    models: dict[str, str]
    reasoning: dict[str, str]
    pricing: dict[str, Price]
    limits: Limits
    checkpoints: Path
    traces: Path
    knowledge_index: Path
    knowledge_dir: Path
    server: Server
    masking_names: tuple[str, ...]
    reference_date: date


def _section(data: dict, name: str) -> dict:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ConfigError(f"config.toml: missing section [{name}]")
    return value


def _string(section: dict, where: str, key: str) -> str:
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"config.toml: [{where}] {key} must be a non-empty string")
    return value


def _positive_int(section: dict, where: str, key: str) -> int:
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"config.toml: [{where}] {key} must be a positive integer")
    return value


def _price_value(section: dict, model: str, key: str) -> float:
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ConfigError(
            f'config.toml: [pricing."{model}"] {key} must be a number >= 0 '
            "(US$ per 1 million tokens)"
        )
    return float(value)


def _absolute_path(section: dict, key: str) -> Path:
    path = Path(_string(section, "server", key))
    if not path.is_absolute():
        raise ConfigError(
            f"config.toml: [server] {key} must be an absolute path, got {str(path)!r}: "
            "the server runs as another process, so a relative path is ambiguous"
        )
    return path


def parse_config(data: dict, root: Path = PROJECT_ROOT) -> Config:
    """Validate the parsed TOML and build the Config. Relative local paths start at `root`."""
    models_section = _section(data, "models")
    models = {role: _string(models_section, "models", role) for role in (*CHAT_ROLES, "embeddings")}
    reasoning_section = _section(data, "reasoning")
    reasoning = {role: _string(reasoning_section, "reasoning", role) for role in CHAT_ROLES}

    pricing_section = _section(data, "pricing")
    pricing: dict[str, Price] = {}
    for role, model in models.items():
        entry = pricing_section.get(model)
        if not isinstance(entry, dict):
            raise ConfigError(
                f'config.toml: no price for model {model!r} ([models] {role}); add [pricing."'
                f'{model}"] so the cost is not shown as zero'
            )
        if role == "embeddings":
            pricing[model] = Price(input=_price_value(entry, model, "input"))
        else:
            pricing[model] = Price(
                input=_price_value(entry, model, "input"),
                cached_input=_price_value(entry, model, "cached_input"),
                output=_price_value(entry, model, "output"),
            )

    limits_section = _section(data, "limits")
    limits = Limits(
        **{
            key: _positive_int(limits_section, "limits", key)
            for key in (
                "max_tokens_per_turn",
                "max_tokens_per_day",
                "recursion_limit",
                "max_output_tokens",
            )
        }
    )
    if limits.max_tokens_per_turn > limits.max_tokens_per_day:
        raise ConfigError(
            "config.toml: [limits] max_tokens_per_turn cannot be greater than max_tokens_per_day"
        )

    paths_section = _section(data, "paths")

    def local_path(key: str) -> Path:
        path = Path(_string(paths_section, "paths", key))
        return path if path.is_absolute() else root / path

    server_section = _section(data, "server")
    server = Server(
        command=_string(server_section, "server", "command"),
        db=_absolute_path(server_section, "JOB_SEARCH_DB"),
        config=(
            _absolute_path(server_section, "JOB_SEARCH_CONFIG")
            if "JOB_SEARCH_CONFIG" in server_section
            else None
        ),
    )

    names = _section(data, "masking").get("names")
    if not isinstance(names, list) or not all(isinstance(n, str) and n.strip() for n in names):
        raise ConfigError("config.toml: [masking] names must be a list of non-empty strings")

    raw_date = _section(data, "demo").get("reference_date")
    try:
        reference_date = (
            raw_date if isinstance(raw_date, date) else date.fromisoformat(str(raw_date))
        )
    except ValueError:
        raise ConfigError(
            "config.toml: [demo] reference_date must be a date (YYYY-MM-DD)"
        ) from None

    return Config(
        models=models,
        reasoning=reasoning,
        pricing=pricing,
        limits=limits,
        checkpoints=local_path("checkpoints"),
        traces=local_path("traces"),
        knowledge_index=local_path("knowledge_index"),
        knowledge_dir=local_path("knowledge_dir"),
        server=server,
        masking_names=tuple(names),
        reference_date=reference_date,
    )


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Config:
    """Read config.toml and the local .env (without overriding variables already set)."""
    load_dotenv(ENV_PATH, override=False)
    try:
        with open(path, "rb") as file:
            data = tomllib.load(file)
    except FileNotFoundError:
        raise ConfigError(
            f"Configuration not found: {path}. Copy config.example.toml to config.toml "
            "and fill in the absolute path of the server database."
        ) from None
    except tomllib.TOMLDecodeError as failure:
        raise ConfigError(f"{path}: invalid TOML: {failure}") from None
    return parse_config(data)
