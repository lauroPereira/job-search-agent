# Tarefa: execução real e evidências

## Objetivo

Registrar o resultado de referência da avaliação com o modelo real, a evidência dos cinco casos de uso com os dados sintéticos, a busca de privacidade e o README atualizado.

## Especificação relacionada

[Especificação](../specs/agente-de-carreira.md), critérios de aceitação: cinco casos de uso com evidência em `docs/evidence/`; resultado de referência com o modelo real; busca nos arquivos versionados não encontra dado real. Questões Q5 e Q6 do [plano](../specs/agente-de-carreira-plano.md).

## Pré-condições

Tarefas 01 a 09 concluídas. Chave da OpenAI do autor disponível localmente (nunca versionada).

## Arquivos prováveis

`evals/agent/results/<data>-<modelo>.md`, `docs/evidence/<data>-verificacao-dos-casos-de-uso.md`, `README.md`, `config.example.toml` (limites, se mudarem).

## Passos

1. Q5: já resolvida na tarefa 01 (dependência na tag `v0.2.0`); só conferir que o `pyproject.toml` continua apontando para a tag.
2. `python -m job_search_agent.evals --real` e versionar o resultado (custo total anotado).
3. Executar os cinco casos de uso na interface com os dados de demonstração (`job-search-agent demo-db`) e a data 2026-03-16; registrar pedidos, rotas, ferramentas, propostas, decisões, tokens e custo, a partir do rastro.
4. Q6: revisar os limites com os números observados e registrar a decisão.
5. Busca de privacidade nos arquivos versionados (e-mail, telefone, CPF e nomes do uso real, com a lista mantida pelo autor fora do repositório) e registro do comando e do resultado.
6. README: premissa de rodar a partir do clone, com instalação editável (`pip install -e ".[dev]"`, ver `config.py`); como instalar, configurar, criar o banco de demonstração (`job-search-agent demo-db`), indexar, abrir a interface e rodar a avaliação; estado da versão.

## Critérios de conclusão

- [ ] Resultado de referência real versionado.
- [ ] Evidência dos cinco casos de uso em `docs/evidence/`, com o nível da verificação (manual, modelo real).
- [ ] Q6 registrada com o que foi feito (Q5 resolvida na tarefa 01).
- [ ] Busca de privacidade registrada sem achados.
- [ ] README coerente com os comandos reais.

## Validação

A preencher.

## Status

```text
pendente
```
