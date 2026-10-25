# Tarefa: grafo, agentes e aprovação

## Objetivo

Montar o grafo LangGraph com roteador, agentes Network e Vagas e o nó de aprovação que pausa com `interrupt` e confirma ou recusa a proposta do servidor, com checkpointer em SQLite e modelo simulado para testes.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seção "Grafo". Critérios da especificação: "Teste: recusar a proposta não altera o banco do servidor"; requisitos de orquestração e de gravação com aprovação.

## Pré-condições

Tarefas 01 a 04 concluídas.

## Arquivos prováveis

`src/job_search_agent/graph.py`, `src/job_search_agent/prompts.py` (versão mínima), `src/job_search_agent/llm.py` (modelo simulado), `tests/test_graph.py`.

## Passos

1. Modelo simulado: subclasse de `BaseChatModel` que devolve mensagens roteirizadas (inclusive `tool_calls` e saída estruturada do roteador) e `usage_metadata`.
2. Estado, nó `route` (saída estruturada; saída inválida vira `out_of_scope`), nó `decline`, nós `network_agent` e `jobs_agent` com `create_agent`, as ferramentas da tarefa 02, `search_knowledge` e o middleware de orçamento.
3. Extração das propostas dos `ToolMessage`; nó `approval` com `interrupt` como primeira instrução; retomada por `Command(resume={proposal_id: "confirm" | "discard"})`; chamadas diretas de `changes_confirm` / `changes_discard`; gravação em `approvals`.
4. `AsyncSqliteSaver` em `data/local/checkpoints.db` e `run_turn(thread_id, text, origin, resume=None)` síncrona (usa `asyncio.run`).

## Critérios de conclusão

- [ ] Teste de integração (servidor real com seed, modelo simulado): proposta de `update_job` recusada; leitura de `list_jobs` antes e depois igual; `approvals.decision = discard`.
- [ ] Teste: proposta confirmada grava no servidor e o resultado aparece na resposta.
- [ ] Teste: pedido roteado para `refuse` não chama nenhuma ferramenta.
- [ ] Teste: `stale_proposal` é mostrado sem nova tentativa.
- [ ] Cada turno grava rota, passos, tokens e custo no rastro.

## Validação

A preencher.

## Status

```text
pendente
```
