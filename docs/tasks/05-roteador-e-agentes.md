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

- [ ] Teste (servidor real com os dados de demonstração de `data/demo`, modelo simulado): pedido de Network chega ao `network_agent` e chama `list_contacts`; pedido de Vagas chega ao `jobs_agent`.
- [ ] Teste: as ferramentas entregues a cada `create_agent` são as da tabela do plano.
- [ ] Teste: pedido roteado para `refuse` não chama nenhuma ferramenta; saída inválida do roteador vira `out_of_scope`.
- [ ] Teste: com `reference_date = "2026-03-16"`, a chamada roteirizada de `daily_summary` recebe essa data e o rastro a registra.
- [ ] Teste: estouro de `recursion_limit` produz a resposta fixa e o status `budget_exceeded`.

## Validação

A preencher.

## Status

```text
pendente
```
