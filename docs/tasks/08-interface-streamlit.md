# Tarefa: interface Streamlit

## Objetivo

Entregar a aplicação Streamlit com o dashboard sem modelo e o chat com um cartão de proposta por vez (confirmar e recusar), entrada bloqueada enquanto houver aprovação pendente, tokens e custo por resposta e o rastro do turno.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seção "Interface Streamlit". Critérios da especificação: "o dashboard não chama modelo (verificável no rastro)"; "toda resposta mostra tokens e custo; o rastro de uma conversa pode ser aberto localmente"; requisito "só confirmar com o clique da pessoa".

## Pré-condições

Tarefas 06 e 07 concluídas.

## Arquivos prováveis

`src/job_search_agent/ui/app.py`, `src/job_search_agent/ui/dashboard.py`, `src/job_search_agent/ui/chat.py`, `src/job_search_agent/cli.py`, `tests/test_dashboard.py`, `tests/test_chat_state.py`.

## Passos

1. `job-search-agent ui` inicia o Streamlit com `ui/app.py` e duas páginas.
2. Dashboard: funções puras que montam os dados a partir de `jobs_funnel_metrics`, `pending_followups`, `daily_summary` (com a data de referência) e do custo diário do rastro; a página só desenha.
3. Chat: histórico, `thread_id` e proposta pendente em `st.session_state`; seletor de origem; data de referência (padrão da configuração de demonstração); chamada a `run_turn`.
4. Cartão da proposta pendente: entidade, campo, valor atual, valor proposto, validade, botões Confirmar e Recusar que retomam o grafo; ao voltar, mostra o resultado e o próximo cartão, se houver.
5. Função pura `input_enabled(state)` que devolve falso enquanto houver proposta pendente; `st.chat_input(disabled=...)` usa essa função.
6. Rodapé de cada resposta com tokens e custo; expansor com o rastro do turno.

## Critérios de conclusão

- [ ] Teste: carregar os dados do dashboard grava só passos `tool` com origem `dashboard`, nenhum `model`.
- [ ] Teste: `input_enabled` é falso com proposta pendente e verdadeiro depois da última decisão.
- [ ] Verificação manual com os dados de demonstração (`job-search-agent demo-db`): um turno com duas propostas mostra um cartão por vez; a entrada fica desabilitada até a última decisão; recusa e confirmação funcionam pelos botões. Anotada aqui (capturas só com dados sintéticos).
- [ ] Toda resposta mostra tokens e custo.

## Validação

A preencher.

## Status

```text
pendente
```
