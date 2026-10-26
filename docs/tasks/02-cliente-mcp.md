# Tarefa: cliente MCP e ferramentas por agente

## Objetivo

Conectar o agente ao servidor job-search-mcp por stdio: `MCPAdapter` (`langchain.mcp`) para listar as ferramentas entregues aos agentes, cada agente só com a sua lista, e `fastmcp.Client` para as chamadas diretas sem modelo (aprovação e dashboard).

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Cliente MCP" e "Grafo" (tabela de ferramentas). Critério da especificação: "Teste: cada agente só vê as ferramentas do seu domínio" (com a exceção de leitura de apoio Q3).

## Pré-condições

Tarefa 01 concluída.

## Arquivos prováveis

`src/job_search_agent/mcp_client.py`, `tests/conftest.py` (fixture do servidor com os dados de demonstração em pasta temporária), `data/demo/*.csv`, `tests/test_mcp_client.py`.

## Passos

1. Fixture de teste: banco temporário com caminho absoluto, criado com `job-search-mcp import data/demo --apply` (ver Decisões), `StdioTransport` com só `JOB_SEARCH_DB` (e `JOB_SEARCH_CONFIG`, se houver) em `env`.
2. `mcp_client.py`: constantes `NETWORK_TOOLS`, `JOBS_TOOLS` (incluindo a leitura de apoio `list_contacts` e `network_company_overview`), `APPROVAL_TOOLS`, `DASHBOARD_TOOLS`, conforme a tabela do plano.
3. `agent_tools(agent)`: abre o `MCPAdapter`, `list_tools()`, devolve só as ferramentas da lista; ferramenta anunciada e não classificada gera erro. Um contexto aberto por turno.
4. `call(tool, **args)`: chamada direta pelo `fastmcp.Client`, devolvendo o conteúdo estruturado.
5. `extract_proposal(tool_message)`: lê `artifact["structured_content"]` (ou o equivalente confirmado na versão instalada) e reconhece `{"proposal": {...}}`.
6. Medir o tempo de partida do servidor e anotar (risco aceito do plano).

## Decisões

- **Dados de demonstração (decisão do Supervisor):** `job-search-mcp --seed` não funciona com o servidor instalado do Git (achado da tarefa 01). O agente traz os próprios dados sintéticos em `data/demo/` (`companies.csv`, `people.csv`, `jobs.csv`, `stages.csv`, `links.csv`, no formato de importação do servidor), copiados sem alteração do seed público da tag `v0.2.0` (`git show v0.2.0:data/seed/<arquivo>`), que é sintético. O banco é criado com `job-search-mcp import data/demo --apply` num arquivo novo apontado por `JOB_SEARCH_DB`: nos testes, pela fixture de `tests/conftest.py`; na demonstração, por `job-search-agent demo-db` (usa o `JOB_SEARCH_DB` de `config.toml` e recusa um arquivo que já existe). Registrado no plano. O `.gitignore` passou a aceitar `data/demo/*.csv`.
- **Um processo por contexto:** o `StdioTransport` é criado com `keep_alive=False`, então o processo do servidor vive enquanto o contexto (`async with adapter(...)` ou `async with client(...)`) estiver aberto: um por turno, como no plano.
- **Executável do servidor:** procurado primeiro ao lado do Python em uso (o `.venv`), depois no `PATH`, porque o processo filho não recebe o ambiente inteiro.
- **Ambiente do servidor:** o SDK de MCP junta ao `env` passado só as variáveis seguras de `get_default_environment()` (por exemplo `PATH` e `SYSTEMROOT`); `OPENAI_API_KEY` não passa (testado com um servidor de prova).
- `changes_list_pending` fica em `UNUSED_TOOLS`: classificada, mas entregue a ninguém, como diz o plano.

- **Ciclo de vida para as próximas tarefas (decisão do Supervisor, revisão do PR 4):** os nós do grafo recebem um `MCPAdapter` já aberto; `changes_confirm` e `changes_discard` usam o `Client` exposto por `MCPAdapter.client`, sem segunda partida do servidor; a interface manterá **um** processo do servidor por processo do Streamlit (`st.cache_resource`, thread com event loop próprio, chamadas por `run_coroutine_threadsafe`, fechamento em `atexit`). A implementar nas tarefas 05, 06 e 08; risco aceito atualizado no plano.

## Critérios de conclusão

- [x] Teste de integração: os nomes entregues a Network e a Vagas são exatamente os da tabela do plano; Vagas recebe `list_contacts` e `network_company_overview` e nenhuma escrita de Network; nenhum agente recebe `changes_*`.
- [x] Teste: as 17 ferramentas anunciadas estão todas classificadas.
- [x] Teste: `add_job` chamado direto devolve proposta e o banco não muda até `changes_confirm`.
- [x] Teste: a variável `OPENAI_API_KEY` não é repassada ao processo do servidor.
- [x] Tempo de partida do servidor anotado na validação.

## Validação

Executada em 2026-10-25, Windows 11, Python 3.12.3, versões da tarefa 01 (sem mudança; conferidas no PyPI no início da tarefa 01, no mesmo dia).

```powershell
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict
# 27 passed (8 em tests/test_mcp_client.py, com o servidor real); ruff: All checks passed
.venv\Scripts\python.exe -m ruff format --check src tests
# 10 files already formatted
```

Testes de `tests/test_mcp_client.py`, todos contra o executável `job-search-mcp` do `.venv`, com banco temporário criado pela importação de `data/demo/`:

- `test_each_agent_gets_exactly_its_tools`: nomes de Network e Vagas iguais à tabela do plano (escrita de novo no teste), leitura de apoio de Vagas presente, nenhuma escrita de Network em Vagas, nenhum `changes_*`.
- `test_all_announced_tools_are_classified`: 17 ferramentas anunciadas, todas classificadas; `test_unclassified_tool_fails`: uma ferramenta tirada da classificação faz `agent_tools` falhar com o nome dela.
- `test_add_job_changes_nothing_until_confirmed`: `add_job` direto (`fastmcp.Client`) devolve `proposal`; `list_jobs` igual antes e depois da proposta; depois de `changes_confirm`, a vaga aparece.
- `test_agent_tool_result_carries_the_proposal`: a ferramenta LangChain do `MCPAdapter` devolve `ToolMessage` com `artifact["structured_content"]["proposal"]`, lida por `extract_proposal`; uma leitura não tem proposta.
- `test_api_key_does_not_reach_the_server`: com `OPENAI_API_KEY` no ambiente do teste, o transporte leva só `JOB_SEARCH_DB`, e um servidor de prova (`tests/env_probe_server.py`) iniciado com esse mesmo transporte não vê a variável.
- `test_demo_db_refuses_existing_database`.

`job-search-agent demo-db` sem `config.toml` sai com código 1 e a mensagem de como criar a configuração.

**Tempo de partida do servidor** (5 medições, `fastmcp.Client` sobre o transporte do projeto, banco de demonstração):

| Etapa | Mediana |
|---|---|
| partida do processo e inicialização da sessão MCP | 2,3 s (2,2 a 2,5 s) |
| primeira chamada (`list_jobs`) | 0,8 s |
| fechamento | 0,3 s |
| `MCPAdapter`: abrir, `list_tools()` e fechar | 3,4 s |
| `job-search-agent demo-db` / importação de `data/demo/` | 2,6 s |

Quase toda a partida é importação de Python (só `import job_search_mcp.server` leva cerca de 2,4 s). Ficou acima da estimativa do plano (menos de 1 s): um turno com aprovação paga duas partidas (cerca de 5 a 7 s só de servidor). Continua sendo o risco aceito do plano; se incomodar na interface, a alternativa registrada é um processo por sessão do Streamlit. Registrado no plano.

**API beta de `langchain.mcp` (langchain 1.4.7):** `from langchain.mcp import MCPAdapter` emite `LangChainBetaWarning`, que é silenciado só na importação em `mcp_client.py`. `MCPAdapter(target)` aceita um `StdioTransport`; `list_tools()` abre o contexto sozinho, e as ferramentas devolvidas são `StructuredTool` com `response_format="content_and_artifact"`; o artefato é `MCPToolArtifact` (`{"structured_content": ...}`), como o plano previa. Um resultado com `isError` vira `ToolMessage` com `status="error"`; o erro de negócio do servidor (`error` e `detail`) volta como resultado normal. O adaptador arma a elicitação com `interrupt()` do LangGraph, sem efeito aqui, porque o servidor não pede entrada. O processo do servidor escreve uma linha `INFO Starting MCP server` no stderr a cada partida.

**Achados da revisão (PR 4), corrigidos no mesmo PR:**

- (Média) `create_demo_db` confere o relatório da importação: cada arquivo de `data/demo/` precisa ter todas as linhas como novas, sem duplicatas nem erros, e a importação precisa dizer que gravou; senão falha e apaga o banco criado (e os arquivos `-wal`, `-shm` e `-journal`). Testes novos: `test_demo_database_has_the_demo_data` (15 vagas, 8 contatos, empresas do seed) e `test_demo_import_with_errors_fails_and_removes_the_database` (uma vaga com nota 99 faz a importação falhar e o banco não fica).
- (Baixa) Docstring de `call`: um resultado com `isError` lança `fastmcp.exceptions.ToolError`; o erro de negócio (`error`/`detail`) volta como está.
- (Baixa) Só `LangChainBetaWarning` é silenciado na importação de `langchain.mcp` (conferido com `python -W error::Warning -c "import job_search_agent.mcp_client"`).
- Decisão de ciclo de vida do processo registrada em "Decisões" e no plano.

Validação depois das correções: `lint_and_tests.py --strict` com 31 testes passando (10 em `tests/test_mcp_client.py`), ruff limpo, `ruff format --check src tests` limpo.

## Status

```text
concluída
```
