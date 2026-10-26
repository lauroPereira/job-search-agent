"""Cost from a fictitious usage and the prices of the example configuration."""

import tomllib
from pathlib import Path

import pytest

from job_search_agent.config import PROJECT_ROOT, parse_config
from job_search_agent.costs import (
    Usage,
    cost_usd,
    day_limit_reached,
    model_cost_usd,
    over_turn_limit,
    usage_from_metadata,
)


@pytest.fixture
def config(tmp_path: Path):
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    return parse_config(data, root=tmp_path)


def test_usage_from_metadata_reads_cached_input() -> None:
    metadata = {
        "input_tokens": 1200,
        "output_tokens": 300,
        "total_tokens": 1500,
        "input_token_details": {"cache_read": 1000},
    }
    assert usage_from_metadata(metadata) == Usage(1200, 300, 1000)
    assert usage_from_metadata(None) == Usage()


def test_cost_with_cached_input(config) -> None:
    # gpt-6.1-sol: input 2.00, cached 0.10, output 10.00 per 1M tokens.
    usage = Usage(input_tokens=1_200_000, output_tokens=100_000, cached_tokens=1_000_000)
    expected = 0.2 * 2.00 + 1.0 * 0.10 + 0.1 * 10.00
    assert model_cost_usd("gpt-6.1-sol", usage, config.pricing) == pytest.approx(expected)


def test_embedding_cost_has_only_input(config) -> None:
    price = config.pricing["text-embedding-3-small"]
    assert cost_usd(Usage(input_tokens=500_000), price) == pytest.approx(0.01)


def test_model_without_price_is_an_error(config) -> None:
    with pytest.raises(KeyError, match="No price for model 'gpt-x'"):
        model_cost_usd("gpt-x", Usage(1, 1), config.pricing)


def test_turn_usage_is_summed_and_compared_with_the_turn_limit(config) -> None:
    calls = [Usage(15_000, 2_000, 10_000), Usage(20_000, 1_500, 18_000), Usage(2_000, 100)]
    turn = sum(calls, Usage())
    assert turn == Usage(37_000, 3_600, 28_000)
    assert turn.total_tokens == 40_600
    assert over_turn_limit(turn, config.limits)  # max_tokens_per_turn = 40000
    assert not over_turn_limit(Usage(30_000, 2_000), config.limits)


def test_day_limit(config) -> None:
    assert not day_limit_reached(399_999, config.limits)
    assert day_limit_reached(400_000, config.limits)
