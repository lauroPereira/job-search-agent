# Tarefa: base do pacote

## Objetivo

Criar o pacote Python `job_search_agent` com dependências fixadas, configuração local e o servidor job-search-mcp como dependência, e confirmar os modelos com uma chamada mínima.

## Especificação relacionada

[`docs/specs/agente-de-carreira-plano.md`](../specs/agente-de-carreira-plano.md) (Decisões técnicas, Componentes afetados). Critério da especificação atendido em parte: "a avaliação roda no CI sem chave de API" (o CI passa a instalar e testar o pacote).

## Pré-condições

- Plano aprovado e integrado em `develop`.
- Versões da tabela do plano conferidas de novo no PyPI; divergência registrada nesta tarefa.

## Arquivos prováveis

`pyproject.toml`, `config.example.toml`, `.env.example`, `.gitignore`, `src/job_search_agent/__init__.py`, `src/job_search_agent/config.py`, `src/job_search_agent/llm.py`, `tests/test_config.py`.

## Passos

1. Criar `pyproject.toml` (Python 3.12, `src/`, dependências com `==` do plano, `job-search-mcp` pelo commit fixado, extra `dev`, script `job-search-agent`, configuração de `ruff` e `pytest`).
2. Criar `config.example.toml` com modelos, esforço de raciocínio, tabela de preços, limites, caminhos em `data/local/`, comando do servidor e `JOB_SEARCH_DB` / `JOB_SEARCH_CONFIG`; e `.env.example` com `OPENAI_API_KEY=`.
3. Garantir no `.gitignore` `config.toml` e `data/local/` (já presente).
4. Implementar `config.py` (lê `config.toml`, falha clara para preço ausente, limite inválido ou caminho relativo do banco).
5. Implementar `llm.py` com `chat_model(role)` e `embeddings()` usando `ChatOpenAI(use_responses_api=True)` e `OpenAIEmbeddings`; nenhum outro módulo importa `langchain_openai`.
6. Testes de `config.py` sem rede.
7. Fora do CI, com a chave do autor: uma chamada mínima a cada modelo configurado e um embedding curto; registrar IDs, tokens e se a chamada de ferramenta funciona pela Responses API.

## Critérios de conclusão

- [ ] `pip install -e ".[dev]"` funciona num ambiente limpo e instala `job-search-mcp` 0.2.0.
- [ ] `python tools/scripts/lint_and_tests.py --strict` passa localmente e no CI, sem `OPENAI_API_KEY`.
- [ ] Configuração inválida produz mensagem clara (testado).
- [ ] Chamada mínima aos dois modelos e ao embedding registrada abaixo, ou a troca de modelo registrada no plano.

## Validação

A preencher pelo Developer: comandos, saídas resumidas, versões instaladas (`pip freeze` dos pacotes do plano).

## Status

```text
pendente
```
