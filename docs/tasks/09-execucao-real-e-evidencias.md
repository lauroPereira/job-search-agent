# Tarefa: execução real e evidências

## Objetivo

Registrar o resultado de referência da avaliação com o modelo real, a evidência dos cinco casos de uso com os dados sintéticos, a busca de privacidade e o README atualizado.

## Especificação relacionada

[Especificação](../specs/agente-de-carreira.md), critérios de aceitação: cinco casos de uso com evidência em `docs/evidence/`; resultado de referência com o modelo real; busca nos arquivos versionados não encontra dado real.

## Pré-condições

Tarefas 01 a 08 concluídas. Chave da OpenAI do autor disponível localmente (nunca versionada). Tag `v0.2.0` do servidor existente, ou registro de que a dependência continua no commit (Q5).

## Arquivos prováveis

`evals/agent/results/<data>-<modelo>.md`, `docs/evidence/<data>-verificacao-dos-casos-de-uso.md`, `README.md`, `pyproject.toml` (troca para a tag `v0.2.0`, se existir).

## Passos

1. Se a tag `v0.2.0` do servidor existir, trocar a referência e rodar os testes.
2. `python -m job_search_agent.evals --real` e versionar o resultado (custo total anotado).
3. Executar os cinco casos de uso na interface com o seed e a data 2026-03-16; registrar pedidos, rotas, ferramentas, propostas, decisões, tokens e custo, a partir do rastro.
4. Revisar os limites de tokens (Q6) com os números observados.
5. Busca de privacidade nos arquivos versionados (e-mail, telefone, CPF, nomes do uso real conhecidos pelo autor, fora do repositório) e registro do comando e do resultado.
6. README: como instalar, configurar, rodar o seed, indexar, abrir a interface e rodar a avaliação; estado da versão.

## Critérios de conclusão

- [ ] Resultado de referência real versionado.
- [ ] Evidência dos cinco casos de uso em `docs/evidence/`, com o nível da verificação (manual, modelo real).
- [ ] Busca de privacidade registrada sem achados.
- [ ] README coerente com os comandos reais.

## Validação

A preencher.

## Status

```text
pendente
```
