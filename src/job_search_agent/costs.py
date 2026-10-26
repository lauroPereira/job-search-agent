"""Tokens and cost of each model call, from the response `usage_metadata`, and the token limits.

No local estimate by tokenizer: what counts is what the API returns. `input_tokens` already
includes the cached input (`input_token_details.cache_read`), which is charged at the
`cached_input` price.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from job_search_agent.config import Limits, Price

PER_TOKENS = 1_000_000  # prices are in US$ per 1 million tokens


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
            self.cached_tokens + other.cached_tokens,
        )


def usage_from_metadata(metadata: Mapping | None) -> Usage:
    """Usage of one response (`AIMessage.usage_metadata`); missing means zero."""
    if not metadata:
        return Usage()
    details = metadata.get("input_token_details") or {}
    return Usage(
        input_tokens=int(metadata.get("input_tokens") or 0),
        output_tokens=int(metadata.get("output_tokens") or 0),
        cached_tokens=int(details.get("cache_read") or 0),
    )


def cost_usd(usage: Usage, price: Price) -> float:
    """Cost in US$ of a usage at a price. An embedding price has only `input`."""
    cached = min(usage.cached_tokens, usage.input_tokens)
    cost = (usage.input_tokens - cached) * price.input
    cost += cached * (price.cached_input if price.cached_input is not None else price.input)
    cost += usage.output_tokens * (price.output or 0.0)
    return cost / PER_TOKENS


def model_cost_usd(model: str, usage: Usage, pricing: Mapping[str, Price]) -> float:
    """Cost of a model call; a model without price is an error, never a zero cost."""
    if model not in pricing:
        raise KeyError(f"No price for model {model!r} in config.toml [pricing]")
    return cost_usd(usage, pricing[model])


def over_turn_limit(usage: Usage, limits: Limits) -> bool:
    """The turn used more than the reference value `max_tokens_per_turn` (it is marked)."""
    return usage.total_tokens > limits.max_tokens_per_turn


def day_limit_reached(tokens_today: int, limits: Limits) -> bool:
    """Checked before each turn: with the day limit reached, the turn does not call a model."""
    return tokens_today >= limits.max_tokens_per_day
