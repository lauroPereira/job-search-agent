"""Trace in SQLite: a turn is recorded in turns and steps, masked; day totals."""

import sqlite3
import tomllib
from datetime import date, datetime
from pathlib import Path

import pytest

from job_search_agent.config import PROJECT_ROOT, parse_config
from job_search_agent.costs import Usage, day_limit_reached, model_cost_usd, over_turn_limit
from job_search_agent.traces import MAX_SUMMARY, TraceStore

DAY = date(2026, 3, 16)


@pytest.fixture
def config(tmp_path: Path):
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    return parse_config(data, root=tmp_path)


@pytest.fixture
def store(config) -> TraceStore:
    return TraceStore(config.traces, config.masking_names)


def at(hour: int, day: date = DAY) -> datetime:
    return datetime(day.year, day.month, day.day, hour).astimezone()


def test_turn_is_recorded_masked_in_turns_and_steps(store: TraceStore, config) -> None:
    turn_id = store.start_turn(
        "thread-1",
        "Registre que falei com Ana Exemplo (ana@example.com, 11 91234-5678) no Banco Aurora",
        origin="conversa",
        reference_date=DAY,
    )
    usage = Usage(1_000, 200, 800)
    cost = model_cost_usd("gpt-6.1-sol", usage, config.pricing)
    store.add_step(turn_id, "model", "gpt-6.1-sol", tokens=usage.total_tokens, cost_usd=cost)
    store.add_step(
        turn_id,
        "tool",
        "log_interaction",
        args={"person": "Ana Exemplo", "summary": "Falou do CPF 123.456.789-09"},
        result={"proposal": {"id": "p-1"}},
        duration_ms=40,
    )
    store.add_step(
        turn_id,
        "approval",
        "log_interaction",
        args={"proposal_id": "p-1", "decision": "confirm", "result": "ok"},
    )
    store.finish_turn(turn_id, "answered", usage, cost, route="network", agent="network_agent")

    turn = store.turn(turn_id)
    assert turn["status"] == "answered" and turn["route"] == "network"
    assert (turn["input_tokens"], turn["output_tokens"], turn["cached_tokens"]) == (1000, 200, 800)
    assert turn["cost_usd"] == pytest.approx(cost)
    assert [(s["seq"], s["kind"]) for s in store.steps(turn_id)] == [
        (1, "model"),
        (2, "tool"),
        (3, "approval"),
    ]

    # Read straight from the file: no personal text unmasked anywhere.
    with sqlite3.connect(config.traces) as connection:
        dump = "\n".join(connection.iterdump())
    for personal in ("Ana Exemplo", "ana@example.com", "91234-5678", "123.456.789-09"):
        assert personal not in dump
    assert "[pessoa]" in dump and "[email]" in dump and "Banco Aurora" in dump


def test_name_with_line_break_is_masked_before_the_json(store: TraceStore) -> None:
    turn_id = store.start_turn("thread-1", "oi")
    store.add_step(
        turn_id, "tool", "log_interaction", args={"notes": ["Falei com Ana\nExemplo hoje"]}
    )
    args = store.steps(turn_id)[0]["args"]
    assert "Ana" not in args and "Exemplo" not in args
    assert args == '{"notes": ["Falei com [pessoa] hoje"]}'


def test_long_step_summary_is_cut(store: TraceStore) -> None:
    turn_id = store.start_turn("thread-1", "oi")
    store.add_step(turn_id, "tool", "list_jobs", result="x" * 2_000)
    assert len(store.steps(turn_id)[0]["result"]) == MAX_SUMMARY


def test_invalid_kind_and_status_are_refused(store: TraceStore) -> None:
    turn_id = store.start_turn("thread-1", "oi")
    with pytest.raises(ValueError, match="step kind"):
        store.add_step(turn_id, "thinking", "x")
    with pytest.raises(ValueError, match="turn status"):
        store.finish_turn(turn_id, "done")


def test_day_limit_is_detected_from_the_trace(store: TraceStore, config) -> None:
    for hour, tokens in ((9, 150_000), (11, 200_000)):
        turn_id = store.start_turn("thread-1", "pedido", started_at=at(hour))
        store.finish_turn(turn_id, "answered", Usage(tokens - 10_000, 10_000))
    other_day = store.start_turn("thread-1", "ontem", started_at=at(9, date(2026, 3, 15)))
    store.finish_turn(other_day, "answered", Usage(300_000, 0))

    assert store.tokens_on(DAY) == 350_000
    assert not day_limit_reached(store.tokens_on(DAY), config.limits)

    turn_id = store.start_turn("thread-1", "mais um", started_at=at(14))
    store.finish_turn(turn_id, "answered", Usage(50_000, 0))
    assert day_limit_reached(store.tokens_on(DAY), config.limits)


def test_turn_above_turn_limit_is_marked(store: TraceStore, config) -> None:
    usage = Usage(39_000, 2_000)
    turn_id = store.start_turn("thread-1", "pedido longo")
    store.finish_turn(
        turn_id, "answered", usage, over_turn_limit=over_turn_limit(usage, config.limits)
    )
    assert store.turn(turn_id)["over_turn_limit"] == 1


def test_cost_by_day(store: TraceStore) -> None:
    for day, cost in ((date(2026, 3, 15), 0.01), (DAY, 0.02), (DAY, 0.03)):
        turn_id = store.start_turn("thread-1", "pedido", started_at=at(10, day))
        store.finish_turn(turn_id, "answered", cost_usd=cost)
    days = store.cost_by_day(date(2026, 3, 1), DAY)
    assert [day for day, _ in days] == ["2026-03-15", "2026-03-16"]
    assert days[1][1] == pytest.approx(0.05)
