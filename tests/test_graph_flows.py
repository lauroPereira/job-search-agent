"""The five flows with the scripted model and the real server over the demo data.

The scripted model does not test the quality of the real model (that is the real evaluation);
these tests check the harness: route followed, tools of the flow allowed and called, arguments
recorded, proposals present or absent.
"""

import json

from test_graph_routing import answer, calls, route_to, run

DAILY_ANSWER = """1. Responder a proposta da Usina Solaris (pendente desde 2026-03-10).
2. Cobrar o retorno do RH do Banco Aurora.
3. Cobrar o resultado do teste técnico da Transportadora Pampa.
4. Enviar a candidatura da Financeira Colibri.
5. Confirmar a indicação no Hospital Arvoredo."""


def tool_steps(traces, turn_id: int) -> list[tuple[str, dict]]:
    return [
        (step["name"], json.loads(step["args"]) if step["args"] else {})
        for step in traces.steps(turn_id)
        if step["kind"] == "tool"
    ]


async def test_daily_round_reads_only_and_proposes_nothing(server, config, traces, knowledge):
    date_args = {"reference_date": "2026-03-16"}
    result, models, _ = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("jobs")],
        agent=[
            calls(("daily_summary", date_args), ("pending_followups", date_args)),
            answer(DAILY_ANSWER),
        ],
        text="O que faço hoje?",
    )
    assert result["route"] == "jobs" and result["status"] == "answered"
    assert result["proposal"] is None
    assert tool_steps(traces, result["turn_id"]) == [
        ("daily_summary", date_args),
        ("pending_followups", date_args),
    ]
    assert len(result["answer"].splitlines()) <= 5
    assert 'Fluxo "rodada diária"' in models["agent"].received[0][0].text


async def test_record_fact_proposes_an_interaction_with_the_origin(
    fresh_server, config, traces, knowledge
):
    result, models, _ = await run(
        fresh_server,
        config,
        traces,
        knowledge,
        router=[route_to("network")],
        agent=[
            calls(("list_contacts", {"company": "Banco Aurora"})),
            calls(
                (
                    "log_interaction",
                    {
                        "contact_id": 1,
                        "date": "2026-03-16",
                        "summary": "Respondeu que vai reforçar a indicação com o RH.",
                    },
                )
            ),
            answer("Preparei a proposta de registro da interação para você confirmar."),
        ],
        text="Print da conversa: ela respondeu hoje que vai reforçar a indicação com o RH.",
        origin="print",
    )
    assert result["route"] == "network"
    assert "Origem do texto da pessoa neste turno: print" in models["agent"].received[0][0].text
    names = [name for name, _ in tool_steps(traces, result["turn_id"])]
    assert names == ["list_contacts", "log_interaction"]
    assert result["status"] == "awaiting_approval"
    assert result["proposal"]["tool"] == "log_interaction"


async def test_evaluate_job_uses_the_supporting_read_and_proposes_the_job(
    fresh_server, config, traces, knowledge
):
    url = "https://vagas.example.com/banco-aurora/analytics-engineer"
    result, _, _ = await run(
        fresh_server,
        config,
        traces,
        knowledge,
        router=[route_to("jobs")],
        agent=[
            calls(
                ("search_knowledge", {"query": "estratégia e notas do Banco Aurora"}),
                ("list_contacts", {"company": "Banco Aurora"}),
            ),
            calls(
                ("add_job", {"company": "Banco Aurora", "title": "Analytics Engineer", "url": url})
            ),
            answer("Nota 8: boa aderência; lacuna em dbt. Você conhece uma pessoa lá."),
        ],
        text=f"Avalie esta vaga: Analytics Engineer no Banco Aurora, {url}",
    )
    steps = tool_steps(traces, result["turn_id"])
    assert ("list_contacts", {"company": "Banco Aurora"}) in steps
    assert [name for name, _ in steps] == ["search_knowledge", "list_contacts", "add_job"]
    assert result["proposal"]["tool"] == "add_job"


async def test_draft_message_reads_facts_and_proposes_nothing(server, config, traces, knowledge):
    draft = "Oi! Passando para saber se há novidades sobre a vaga de Analytics Engineer."
    result, _, _ = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("network")],
        agent=[calls(("list_contacts", {"company": "Loja Horizonte"})), answer(draft)],
        text="Escreva um follow-up para o recrutador da Loja Horizonte",
    )
    assert result["route"] == "network" and result["status"] == "answered"
    assert result["proposal"] is None and result["answer"] == draft


async def test_prepare_interview_searches_the_knowledge_base(server, config, traces, knowledge):
    result, _, _ = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("jobs")],
        agent=[
            calls(
                ("list_jobs", {}),
                ("search_knowledge", {"query": "entrevista com o gestor", "kind": "case"}),
            ),
            answer(
                "Pauta: use o case de conflito de prioridades "
                "[fonte: data/knowledge/case-conflito-de-prioridades.md § Ação]."
            ),
        ],
        text="Prepare a entrevista com o gestor da Editora Farol",
    )
    names = [name for name, _ in tool_steps(traces, result["turn_id"])]
    assert names == ["list_jobs", "search_knowledge"]
    assert result["proposal"] is None and "[fonte:" in result["answer"]


async def test_missing_data_asks_and_proposes_nothing(server, config, traces, knowledge):
    result, _, _ = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("jobs")],
        agent=[
            calls(("list_jobs", {})),
            answer("Qual foi o tipo de etapa (RH, técnica ou gestor) e em que data?"),
        ],
        text="Registre que fiz uma entrevista no Banco Aurora",
    )
    assert result["route"] == "jobs" and result["status"] == "answered"
    assert result["proposal"] is None and "?" in result["answer"]
    assert [name for name, _ in tool_steps(traces, result["turn_id"])] == ["list_jobs"]


async def test_send_request_is_refused_without_tools(server, config, traces, knowledge):
    result, _, given = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("refuse")],
        agent=[],
        text="Envie esta mensagem para a recrutadora",
    )
    assert result["route"] == "refuse" and result["status"] == "declined"
    assert given == {} and tool_steps(traces, result["turn_id"]) == []
