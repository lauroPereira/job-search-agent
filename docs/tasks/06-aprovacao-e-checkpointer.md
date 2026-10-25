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

- [ ] Teste de integração (servidor real com seed, modelo simulado): proposta de `update_job` recusada; leitura de `list_jobs` antes e depois igual; passo `approval` com `discard`.
- [ ] Teste: proposta confirmada grava no servidor e o resultado aparece na resposta.
- [ ] Teste: duas propostas no mesmo turno geram dois `interrupt` em sequência; confirmar a primeira e recusar a segunda grava só a primeira.
- [ ] Teste: `stale_proposal` é mostrado sem nova tentativa.
- [ ] Teste: retomar um `thread_id` depois de recriar o grafo (novo processo) encontra a proposta pendente no checkpointer.

## Validação

A preencher.

## Status

```text
pendente
```
