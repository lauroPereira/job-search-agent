# Tarefa: aprovação e checkpointer

## Objetivo

Acrescentar ao grafo o nó de aprovação, que pausa com um `interrupt` por proposta, em sequência, e confirma ou recusa pelo servidor, com checkpointer em SQLite e a função `run_turn` usada pela interface.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seção "Grafo" (aprovação, checkpointer). Critério da especificação: "Teste: recusar a proposta não altera o banco do servidor"; requisitos de gravação com aprovação.

## Pré-condições

Tarefa 05 concluída.

## Arquivos prováveis

`src/job_search_agent/graph.py`, `tests/test_graph_approval.py`.

## Passos

1. Nó `approval`: `interrupt({"proposal": pending[0]})` como primeira instrução, sem `try/except` em volta; depois, `changes_confirm` ou `changes_discard` pelo `fastmcp.Client`; proposta movida para `decided`; passo `approval` no rastro.
2. Aresta condicional: volta a `approval` enquanto houver `pending`; senão, fim do turno com a mensagem de resultado.
3. `stale_proposal` e `expired_proposal` mostrados sem nova tentativa.
4. `AsyncSqliteSaver` em `data/local/checkpoints.db`; `run_turn(thread_id, text=None, origin, reference_date, resume=None)` síncrona (usa `asyncio.run`), que devolve a resposta, a proposta pendente (se houver), tokens e custo.

## Critérios de conclusão

- [x] Teste de integração (servidor real com os dados de demonstração de `data/demo`, modelo simulado): proposta de `update_job` recusada; leitura de `list_jobs` antes e depois igual; passo `approval` com `discard`.
- [x] Teste: proposta confirmada grava no servidor e o resultado aparece na resposta.
- [x] Teste: duas propostas no mesmo turno geram dois `interrupt` em sequência; confirmar a primeira e recusar a segunda grava só a primeira.
- [x] Teste: `stale_proposal` é mostrado sem nova tentativa.
- [x] Teste: retomar um `thread_id` depois de recriar o grafo (novo processo) encontra a proposta pendente no checkpointer.

## Validação

Executada em 2026-10-25, Windows 11, `.venv` com Python 3.12 (versões da tarefa 01, sem mudança). Sem chave da OpenAI: modelo simulado (`ScriptedChatModel`) e servidor real (`job-search-mcp` v0.2.0) sobre bancos temporários com os dados de `data/demo/`.

**Implementação** (`src/job_search_agent/graph.py`, `src/job_search_agent/prompts.py`)

- Nó `approval`: `interrupt({"proposal": pending[0]})` é a primeira instrução, sem `try/except` em volta; só depois da retomada chama `changes_confirm` ou `changes_discard` pelo `Client` do adaptador já aberto (`MCPAdapter.client`, sem segunda partida do servidor), grava o passo `approval` no rastro (`name` = ferramenta proposta; `args` com `proposal_id`, `decision` e o código do resultado), move a proposta para `decided` e devolve uma mensagem para a pessoa. Decisão diferente de `confirm` ou `discard` é erro.
- Aresta condicional depois dos agentes e do próprio `approval`: volta a `approval` enquanto houver `pending`; senão, fim. Um `interrupt` por proposta, em sequência.
- Mensagens (`prompts.decision_message`): confirmado, com as mudanças da proposta (`entidade.campo = valor`); recusado ("nada foi gravado"); `stale_proposal` e `expired_proposal` explicados, sem nova tentativa automática; outro erro de negócio com código e detalhe; `ToolError` (falha de protocolo ou do servidor) vira `tool_error` com aviso de que não se sabe se a decisão foi aplicada.
- `open_checkpointer(path)`: `AsyncSqliteSaver.from_conn_string` em `data/local/checkpoints.db` (cria a pasta), aberto enquanto em uso. Sem checkpointer, `build_graph` usa `InMemorySaver` (o `interrupt` precisa de um).
- `input_enabled(state)`: falso enquanto houver proposta pendente; a interface (tarefa 08) desabilita o `chat_input` com isso.
- `arun_turn(..., text=None, resume=None)`: novo turno (zera `pending`, `decided` e `usage`) ou retomada com `Command(resume="confirm" | "discard")` no mesmo `turn_id` (lido do checkpointer); retomada sem proposta pendente é recusada. Devolve resposta, status, rota, agente, a próxima proposta (ou `None`), as decididas e tokens e custo do turno; o turno é fechado no rastro a cada chamada (status final `answered` depois da última decisão).

**Decisões**

- `run_turn` síncrona com `asyncio.run` não foi feita: a decisão do Supervisor (um processo do servidor por processo do Streamlit, thread com event loop próprio e `run_coroutine_threadsafe`) torna `asyncio.run` por turno incompatível com o adaptador aberto, que pertence ao loop dessa thread. A interface (tarefa 08) chama `arun_turn` no loop persistente. Registrado como pendência.
- As fixtures `config`, `knowledge` e `traces` passaram para `tests/conftest.py`, usadas pelos testes das tarefas 05 e 06.

**Testes** (`tests/test_graph_approval.py`, 7 testes, servidor real com `data/demo/`):

- recusa: proposta de `update_job` recusada; `list_jobs` antes e depois igual; passo `approval` com `discard`; `input_enabled` falso com a proposta pendente e verdadeiro depois;
- confirmação: grava no servidor (status da vaga muda) e a resposta traz "Confirmado (update_job)" com o valor novo;
- duas propostas no mesmo turno (`update_job` e `add_job`): dois `interrupt` em sequência; confirmar a primeira e recusar a segunda grava só a primeira; dois passos `approval` na ordem;
- `stale_proposal`: duas propostas sobre a mesma vaga; confirmar as duas grava a primeira e mostra a segunda como desatualizada, com só dois passos `approval` (sem nova tentativa);
- `ToolError` na decisão vira `tool_error` com mensagem clara;
- retomada depois de reabrir o checkpointer SQLite (nova conexão, novo adaptador, novo grafo, nenhum modelo): a proposta pendente está lá e a confirmação grava, no mesmo `turn_id`;
- retomada sem proposta pendente é recusada.

```text
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict   -> 82 passed; ruff limpo; validação estrita sem falhas
.venv\Scripts\python.exe -m ruff format --check src tests          -> 22 files already formatted
python -W error::Warning -c "import job_search_agent.graph"         -> sem aviso
```

**Pendências**

- Chamada síncrona para a interface sobre o loop persistente (no lugar de `run_turn` com `asyncio.run`): tarefa 08.
- Verificação com o modelo real (chave do autor): tarefas 07 e 10.

## Status

```text
concluída
```
