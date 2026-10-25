# Tarefa: interface Streamlit

## Objetivo

Entregar a aplicação Streamlit com o dashboard sem modelo e o chat com cartão de proposta (confirmar e recusar), tokens e custo por resposta e o rastro do turno.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seção "Interface Streamlit". Critérios da especificação: "o dashboard não chama modelo (verificável no rastro)"; "toda resposta mostra tokens e custo; o rastro de uma conversa pode ser aberto localmente".

## Pré-condições

Tarefas 05 e 06 concluídas.

## Arquivos prováveis

`src/job_search_agent/ui/app.py`, `src/job_search_agent/ui/dashboard.py`, `src/job_search_agent/ui/chat.py`, `src/job_search_agent/cli.py`, `tests/test_dashboard.py`.

## Passos

1. `job-search-agent ui` inicia o Streamlit com `ui/app.py` e duas páginas.
2. Dashboard: funções puras que montam os dados a partir de `jobs_funnel_metrics`, `pending_followups`, `daily_summary` e do custo diário do rastro; a página só desenha.
3. Chat: histórico e `thread_id` em `st.session_state`, seletor de origem, data de referência opcional, chamada a `run_turn`.
4. Cartão de proposta por proposta: entidade, campo, valor atual, valor proposto, validade, botões Confirmar e Recusar que retomam o grafo.
5. Rodapé de cada resposta com tokens e custo; expansor com o rastro do turno.

## Critérios de conclusão

- [ ] Teste: carregar os dados do dashboard grava só passos `tool` com origem `dashboard`, nenhum `model`.
- [ ] Verificação manual com o seed e o modelo simulado ou real: proposta mostrada, recusa e confirmação funcionam pelos botões; anotada aqui com descrição (capturas só com dados sintéticos).
- [ ] Toda resposta mostra tokens e custo.

## Validação

A preencher.

## Status

```text
pendente
```
