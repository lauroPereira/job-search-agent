# Tarefa: roteador e agentes

## Objetivo

Montar a primeira parte do grafo LangGraph: modelo simulado, roteador com saída estruturada, nó `decline` e agentes Network e Vagas com as suas ferramentas, a data de referência e o limite por turno.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Grafo" e "Custo". Requisitos de orquestração da especificação; critério "cada agente só vê as ferramentas do seu domínio".

## Pré-condições

Tarefas 01 a 04 concluídas.

## Arquivos prováveis

`src/job_search_agent/graph.py`, `src/job_search_agent/prompts.py` (versão mínima), `src/job_search_agent/llm.py` (modelo simulado), `tests/test_graph_routing.py`.

## Passos

1. Modelo simulado: subclasse de `BaseChatModel` que devolve mensagens roteirizadas (inclusive `tool_calls` e a saída estruturada do roteador) e `usage_metadata`.
2. Estado do plano; nó `route` (saída inválida vira `out_of_scope`); nó `decline` com respostas fixas; verificação do limite do dia antes de `route`.
3. Nós `network_agent` e `jobs_agent` com `create_agent`, as ferramentas da tarefa 02 e `search_knowledge`, invocados com `recursion_limit` e `max_output_tokens` da configuração; `GraphRecursionError` vira a resposta fixa com status `budget_exceeded`.
4. `reference_date` no prompt de sistema e instrução de passá-la às ferramentas de data.
5. Extração das propostas dos `ToolMessage` para `pending` (sem o nó de aprovação ainda: o turno termina com `awaiting_approval`).
6. Gravação de rota, passos, tokens e custo no rastro.

## Critérios de conclusão

- [x] Teste (servidor real com os dados de demonstração de `data/demo`, modelo simulado): pedido de Network chega ao `network_agent` e chama `list_contacts`; pedido de Vagas chega ao `jobs_agent`.
- [x] Teste: as ferramentas entregues a cada `create_agent` são as da tabela do plano.
- [x] Teste: pedido roteado para `refuse` não chama nenhuma ferramenta; saída inválida do roteador vira `out_of_scope`.
- [x] Teste: com `reference_date = "2026-03-16"`, a chamada roteirizada de `daily_summary` recebe essa data e o rastro a registra.
- [x] Teste: estouro de `recursion_limit` produz a resposta fixa e o status `budget_exceeded`.

## Validação

Executada em 2026-10-25, Windows 11, `.venv` com Python 3.12 (versões da tarefa 01, sem mudança). Sem chave da OpenAI: tudo com o modelo simulado e o servidor real (`job-search-mcp` v0.2.0) sobre um banco temporário com os dados de `data/demo/`.

**Implementação**

- `llm.py`: `ScriptedChatModel(BaseChatModel)` devolve, em ordem, as mensagens do roteiro (`tool_calls` e `usage_metadata` inclusos), guarda em `received` cada lista de mensagens recebida e tem `bind_tools` que devolve o próprio modelo. O mesmo roteiro serve ao `create_agent` e à saída estruturada do roteador (uma chamada de ferramenta com o nome do esquema). Sem roteiro restante, falha com mensagem clara.
- `prompts.py` (versão mínima): instruções do roteador com as quatro rotas, instruções comuns curtas, `agent_prompt(agent, reference_date)` com "Hoje é AAAA-MM-DD" e a instrução de passar `reference_date` a `daily_summary`, `pending_followups` e `jobs_funnel_metrics` (e como `date` quando a pessoa disser "hoje"), respostas fixas de `decline` (`refuse`, `out_of_scope`, `day_limit`) e a resposta de passos demais. Os fluxos e as regras completas são da tarefa 07.
- `graph.py`:
  - `build_graph(config, models, mcp, knowledge, traces, checkpointer=None)` recebe um `MCPAdapter` **já aberto**; as ferramentas de cada agente (`mcp_client.agent_tools` mais `search_knowledge`) são listadas uma vez na montagem; nenhum nó abre servidor.
  - Estado `TurnState`: `messages`, `route`, `agent`, `origin`, `reference_date`, `pending`, `usage` (total do turno), `turn_id`, `status`. `decided` fica para a tarefa 06.
  - `check_day_limit` (antes de `route`): soma do dia em `traces.db` (data local de hoje) contra `max_tokens_per_day`; excedido, vai a `decline` com a resposta fixa, status `budget_exceeded`, sem chamar modelo.
  - `route`: `with_structured_output(RouteDecision, include_raw=True)` com `route: Literal["network", "jobs", "refuse", "out_of_scope"]`; o roteador vê só as instruções e o último pedido. Saída não reconhecida (texto, rota fora da lista) vira `out_of_scope`.
  - `decline`: resposta fixa por código, status `declined`; sem modelo de redação e sem ferramentas.
  - `network_agent` e `jobs_agent`: `create_agent(model, tools, system_prompt=agent_prompt(...), name=...)` criado a cada turno (o prompt leva a data do turno), executado com `astream(..., stream_mode="values")` e `recursion_limit` da configuração; `max_output_tokens` já vem de `llm.chat_model`. Em `GraphRecursionError`, a resposta é a fixa e o status `budget_exceeded`; os passos já feitos vão para o rastro, mas não para a conversa (uma chamada de ferramenta sem resultado quebraria o turno seguinte).
  - Propostas extraídas dos `ToolMessage` (`extract_proposal`) vão para `pending`; com alguma, o turno termina em `awaiting_approval`.
  - Rastro: um passo `model` por resposta de modelo (nome do modelo, tokens, custo pela tabela de preços, chamadas pedidas) e um passo `tool` por resultado (argumentos da chamada e texto do resultado, mascarados e resumidos).
  - `arun_turn(graph, traces, config, text, thread_id=..., reference_date=..., origin=...)` (assíncrona) abre o turno no rastro, executa o grafo e fecha com status, rota, agente, tokens, custo e `over_turn_limit`; uma exceção fecha o turno como `error`. A versão síncrona com checkpointer (`run_turn`) é da tarefa 06.

**Decisões**

- `agent` no estado e no rastro é o nome do nó (`network_agent`, `jobs_agent`), também passado como `name` ao `create_agent`.
- O agente é recriado a cada turno (barato: só compila o grafo interno) para levar a data de referência no prompt de sistema; as ferramentas não são relistadas.
- O roteador recebe só o último pedido, sem o histórico, para manter o roteamento simples e barato.

**Testes** (`tests/test_graph_routing.py`, 8 testes, servidor real com `data/demo/`):

- pedido de Network → `network_agent`, que chama `list_contacts` no servidor real; passos `model` (roteador), `model`, `tool list_contacts`, `model` no rastro; nome do contato mascarado no resultado; tokens e custo do turno gravados;
- pedido de Vagas → `jobs_agent`; o prompt de sistema recebido pelo modelo tem "Hoje é 2026-03-16"; a chamada roteirizada de `daily_summary` tem `reference_date = "2026-03-16"` no rastro, e o resultado do servidor é dessa data; `turns.reference_date` registrado;
- ferramentas entregues a cada `create_agent` (espião em `graph.create_agent`) iguais à tabela do plano, escrita de novo no teste, mais `search_knowledge`;
- `add_job` gera proposta em `pending` e status `awaiting_approval` (banco novo);
- rota `refuse`, texto sem saída estruturada e rota fora da lista: `decline`, nenhum agente criado, nenhuma ferramenta, só o passo do roteador;
- estouro de `recursion_limit` (agente roteirizado em laço de `list_contacts`): resposta fixa e status `budget_exceeded`, tokens gravados;
- limite do dia já atingido no rastro: resposta fixa, nenhum modelo chamado, nenhum passo.

```text
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict   -> 75 passed; ruff limpo; validação estrita sem falhas
.venv\Scripts\python.exe -m ruff format --check src tests          -> 21 files already formatted
python -W error::Warning -c "import job_search_agent.graph"         -> sem aviso
```

**Pendências**

- Conferir com o modelo real (chave do autor) a saída estruturada do roteador pela Responses API e a chamada de ferramentas MCP pelo `gpt-6.1-sol` (risco do plano) — tarefa 10, ou antes, na verificação manual da tarefa 07.
- Nó de aprovação, checkpointer e `run_turn` síncrona — tarefa 06.

## Status

```text
concluída
```
