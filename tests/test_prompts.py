"""Instructions: rules of decision 0002 in both agents, the five flows and the fixed answers."""

import re

import pytest

from job_search_agent import prompts
from job_search_agent.knowledge import NO_BASIS

# One phrase per rule, as written in the common instructions.
RULES = {
    "facts from the server, not memory": "Fatos vêm do servidor, não da memória",
    "do not invent": "Não invente status, datas ou valores",
    "ask when data is missing": "pergunte de forma objetiva e não proponha nada",
    "writes are proposals": "Toda gravação é uma proposta",
    "no external action": "não envia, não publica, não faz login",
    "no tests": "não responde\n   testes ou provas",
    "never say it sent": "nunca diga que enviou",
    "authorship honesty": "Honestidade de autoria",
    "discretion": "não cite um contato como fonte de informação para outro",
    "citation": "[fonte: data/knowledge/arquivo.md § título]",
    "no basis": NO_BASIS,
}


@pytest.mark.parametrize("agent", ["network", "jobs"])
@pytest.mark.parametrize("rule", sorted(RULES))
def test_each_rule_is_in_both_agents(agent: str, rule: str) -> None:
    assert RULES[rule] in prompts.agent_prompt(agent, "2026-03-16")


def test_reference_date_and_origin_are_in_the_prompt() -> None:
    prompt = prompts.agent_prompt("jobs", "2026-03-16", "print")
    assert "Hoje é 2026-03-16" in prompt
    assert all(tool in prompt for tool in prompts.DATE_TOOLS)
    assert "Origem do texto da pessoa neste turno: print" in prompt


def test_flows_are_attached_to_the_responsible_agent() -> None:
    jobs = prompts.agent_prompt("jobs", "2026-03-16")
    network = prompts.agent_prompt("network", "2026-03-16")
    for flow in ("rodada diária", "registrar fato", "avaliar vaga", "redigir mensagem"):
        assert f'Fluxo "{flow}"' in jobs
    assert 'Fluxo "preparar entrevista"' in jobs
    assert 'Fluxo "registrar fato"' in network and 'Fluxo "redigir mensagem"' in network
    assert 'Fluxo "rodada diária"' not in network
    # Daily round: at most five actions and no write; evaluate job uses the supporting read.
    assert "no máximo cinco ações" in jobs and "Não grave nada nesta rodada" in jobs
    assert "list_contacts com company" in jobs


def test_router_has_an_example_of_each_route_and_the_four_refusals() -> None:
    for route in ("network:", "jobs:", "refuse:", "out_of_scope:"):
        assert route in prompts.ROUTER
    for request in (
        "envie esta mensagem para a recrutadora",
        "faça login no LinkedIn e se candidate à vaga",
        "aceite os termos do processo seletivo por mim",
        "responda este teste técnico da vaga",
    ):
        assert request in prompts.ROUTER
    assert "Redigir um texto para a pessoa enviar NÃO é refuse" in prompts.ROUTER


PROMISES = re.compile(
    r"\b(vou enviar|enviei|enviado|enviarei|publiquei|vou publicar|fiz login|"
    r"me candidatei|vou me candidatar|aceitei|respondi)\b",
    re.IGNORECASE,
)


@pytest.mark.parametrize("code", sorted(prompts.DECLINE))
def test_decline_answers_promise_no_external_action(code: str) -> None:
    assert not PROMISES.search(prompts.DECLINE[code])


def test_refusal_says_what_the_person_can_do() -> None:
    assert "fica com você" in prompts.DECLINE["refuse"]
    assert "Posso redigir" in prompts.DECLINE["refuse"]
