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
2. Criar `config.example.toml` com modelos, esforço de raciocínio, tabela de preços, limites, caminhos em `data/local/`, comando do servidor, `JOB_SEARCH_DB` / `JOB_SEARCH_CONFIG`, `[masking] names` com os nomes fictícios do seed e `[demo] reference_date = "2026-03-16"`; e `.env.example` com `OPENAI_API_KEY=`.
3. Garantir no `.gitignore` `config.toml` e `data/local/` (já presente).
4. Implementar `config.py` (lê `config.toml`, falha clara para preço ausente, limite inválido ou caminho relativo do banco).
5. Implementar `llm.py` com `chat_model(role)` e `embeddings()` usando `ChatOpenAI(use_responses_api=True)` e `OpenAIEmbeddings`; nenhum outro módulo importa `langchain_openai`.
6. Testes de `config.py` sem rede.
7. Fora do CI, com a chave do autor: uma chamada mínima a cada modelo configurado e um embedding curto; registrar IDs, tokens e se a chamada de ferramenta funciona pela Responses API.

## Critérios de conclusão

- [x] `pip install -e ".[dev]"` funciona num ambiente limpo e instala `job-search-mcp` 0.2.0.
- [x] `python tools/scripts/lint_and_tests.py --strict` passa localmente e no CI, sem `OPENAI_API_KEY`. (Localmente confirmado; no CI, conferido no PR.)
- [x] Configuração inválida produz mensagem clara (testado).
- [ ] Chamada mínima aos dois modelos e ao embedding registrada abaixo, ou a troca de modelo registrada no plano. **Pendente: aguarda a chave do autor.**

## Validação

Executada em 2026-10-25, Windows 11, num ambiente virtual novo.

**Ambiente e instalação**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Instalou sem erro. Python 3.12.3. Versões instaladas (`pip freeze`, pacotes do plano e transitivas principais):

```text
langgraph==1.2.17
langgraph-checkpoint-sqlite==3.1.2
langchain==1.4.7
langchain-core==1.7.0
langchain-openai==1.7.2
streamlit==1.66.1
python-dotenv==1.2.4
job-search-mcp @ git+https://github.com/lauroPereira/job-search-mcp.git@4cb4759a998d9531dd74849499a36200217a34ed   (tag v0.2.0; __version__ 0.2.0)
pytest==9.1.1
pytest-asyncio==1.4.0
ruff==0.17.2
fastmcp==4.1.0
mcp==2.3.0
openai==3.37.0
```

Versões conferidas no PyPI em 2026-10-25: todas iguais ao plano, exceto `pytest-asyncio`, que já tem a 1.4.1; ficou a 1.4.0 do plano (disponível e compatível), sem motivo para trocar nesta tarefa.

**Dependência do servidor (Q5):** a tag pública `v0.2.0` do job-search-mcp existe; a dependência foi fixada na tag (`job-search-mcp @ git+https://github.com/lauroPereira/job-search-mcp.git@v0.2.0`), por decisão do Supervisor, e o plano foi atualizado.

**Testes e lint, sem `OPENAI_API_KEY`**

```powershell
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict
# 19 passed; ruff: All checks passed; "Validação estrita concluída sem falhas."
.venv\Scripts\python.exe -m ruff format --check src tests
# 6 files already formatted
```

`ruff format --check .` acusa só `tools/scripts/lint_and_tests.py`, arquivo gerido pelo template e anterior a esta tarefa; não foi alterado (o CI não roda `ruff format`).

Testes (`tests/test_config.py`, `tests/test_llm.py`): o `config.example.toml` é válido; preço ausente (modelo inteiro ou só `output`), limite inválido (0, negativo, booleano, texto, decimal), limite por turno acima do diário, caminho relativo em `JOB_SEARCH_DB` ou `JOB_SEARCH_CONFIG`, seção ausente, data inválida, arquivo ausente e TOML inválido produzem `ConfigError` com seção e chave; o ambiente do servidor só leva `JOB_SEARCH_DB` e `JOB_SEARCH_CONFIG`; `chat_model` monta `ChatOpenAI` com `use_responses_api=True`, esforço de raciocínio e `max_tokens` da configuração, sem rede; o teste de fumaça sem chave não chama a API e devolve 2.

**Chamada real (passo 7): pendente, aguarda a chave do autor.** Não há chave disponível; nenhuma chave foi procurada nem gravada. Comando preparado, para rodar fora do CI com `OPENAI_API_KEY` em `.env` e um `config.toml` local:

```powershell
.venv\Scripts\python.exe -m job_search_agent.llm --smoke
```

Ele chama cada modelo de chat (`router` e `agent`) uma vez sem ferramenta e uma vez com uma ferramenta de eco, imprimindo o modelo pedido e o devolvido, o texto, `tool_calls` e `usage_metadata`, e gera um embedding curto, imprimindo o modelo e as dimensões. O resultado deve ser registrado aqui (ou a troca de modelo, no plano).

**Achado para a tarefa 02:** `job-search-mcp --seed` não funciona com o servidor instalado do Git (instalação não editável): o servidor procura `data/seed/` relativo ao pacote (`.venv\Lib\data\seed`) e recusa com "install from a clone, with pip install -e .". O plano prevê os testes de integração com `--seed`; a forma de carregar o seed sintético fica para decisão do Supervisor na tarefa 02.

## Status

```text
concluída, exceto o critério da chamada real (aguarda a chave do autor)
```
