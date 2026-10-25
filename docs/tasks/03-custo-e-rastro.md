# Tarefa: mascaramento, custo, limites e rastro

## Objetivo

Calcular tokens e custo de cada chamada de modelo, aplicar os limites por turno e por dia e gravar o rastro mascarado em SQLite.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Custo" e "Rastro local". Critérios da especificação: "toda resposta mostra tokens e custo; o rastro de uma conversa pode ser aberto localmente"; requisito não funcional de privacidade (logs mascaram dados pessoais).

## Pré-condições

Tarefa 01 concluída.

## Arquivos prováveis

`src/job_search_agent/masking.py`, `src/job_search_agent/costs.py`, `src/job_search_agent/traces.py`, `tests/test_masking.py`, `tests/test_costs.py`, `tests/test_traces.py`.

## Passos

1. `masking.py`: e-mail, telefone, CPF e números longos, links de perfil pessoal e nomes conhecidos (lista recebida, comparação sem acento e sem maiúscula).
2. `costs.py`: custo a partir de `usage_metadata` (entrada, entrada em cache, saída) e da tabela de preços; soma por turno; verificação dos limites.
3. Middleware de orçamento (`AgentMiddleware.before_model`, `jump_to: "end"`) com mensagem fixa.
4. `traces.py`: criação das tabelas `turns`, `steps`, `approvals`; gravação mascarada; total de tokens do dia; custo por dia para o dashboard.

## Critérios de conclusão

- [ ] Testes de mascaramento com exemplos sintéticos de cada padrão.
- [ ] Teste de custo com uso fictício e preços da configuração (incluindo entrada em cache).
- [ ] Teste: limite do dia excedido impede o turno sem chamar modelo; limite do turno encerra o agente com a mensagem fixa.
- [ ] Teste: um turno gravado aparece em `turns` e `steps`, sem texto pessoal não mascarado.

## Validação

A preencher.

## Status

```text
pendente
```
