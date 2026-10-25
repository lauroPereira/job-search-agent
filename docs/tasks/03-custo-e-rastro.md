# Tarefa: mascaramento, custo, limites e rastro

## Objetivo

Calcular tokens e custo de cada chamada de modelo, preparar os limites por turno e por dia e gravar o rastro mascarado em SQLite.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Custo" e "Rastro local". Critérios da especificação: "toda resposta mostra tokens e custo; o rastro de uma conversa pode ser aberto localmente"; requisito não funcional de privacidade (logs mascaram dados pessoais).

## Pré-condições

Tarefa 01 concluída.

## Arquivos prováveis

`src/job_search_agent/masking.py`, `src/job_search_agent/costs.py`, `src/job_search_agent/traces.py`, `config.example.toml` (`[masking] names`, `[limits]`), `tests/test_masking.py`, `tests/test_costs.py`, `tests/test_traces.py`.

## Passos

1. `masking.py`: e-mail, telefone, CPF e números longos, links de perfil pessoal e os nomes de `[masking] names` da configuração (comparação sem acento e sem maiúscula). No exemplo de configuração, os nomes fictícios do seed.
2. `costs.py`: custo a partir de `usage_metadata` (entrada, entrada em cache, saída) e da tabela de preços; soma por turno; comparação com `max_tokens_per_turn`; verificação de `max_tokens_per_day`.
3. Configuração dos limites: `recursion_limit`, `max_output_tokens`, `max_tokens_per_turn`, `max_tokens_per_day` (valores iniciais do plano).
4. `traces.py`: tabelas `turns` e `steps` (decisões de aprovação como `kind = approval`); gravação mascarada; total de tokens do dia; custo por dia para o dashboard.

## Critérios de conclusão

- [ ] Testes de mascaramento com exemplos sintéticos de cada padrão e de um nome da lista.
- [ ] Teste de custo com uso fictício e preços da configuração (incluindo entrada em cache).
- [ ] Teste: limite do dia excedido é detectado a partir do rastro; uso do turno acima de `max_tokens_per_turn` é marcado.
- [ ] Teste: um turno gravado aparece em `turns` e `steps`, sem texto pessoal não mascarado.

## Validação

A preencher.

## Status

```text
pendente
```
