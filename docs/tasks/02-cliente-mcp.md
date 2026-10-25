# Tarefa: cliente MCP e ferramentas por agente

## Objetivo

Conectar o agente ao servidor job-search-mcp por stdio: `MCPAdapter` (`langchain.mcp`) para listar as ferramentas entregues aos agentes, cada agente só com a sua lista, e `fastmcp.Client` para as chamadas diretas sem modelo (aprovação e dashboard).

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Cliente MCP" e "Grafo" (tabela de ferramentas). Critério da especificação: "Teste: cada agente só vê as ferramentas do seu domínio" (com a exceção de leitura de apoio Q3).

## Pré-condições

Tarefa 01 concluída.

## Arquivos prováveis

`src/job_search_agent/mcp_client.py`, `tests/conftest.py` (fixture do servidor com seed em pasta temporária), `tests/test_mcp_client.py`.

## Passos

1. Fixture de teste: banco temporário com caminho absoluto, `job-search-mcp --seed`, `StdioTransport` com só `JOB_SEARCH_DB` (e `JOB_SEARCH_CONFIG`, se houver) em `env`.
2. `mcp_client.py`: constantes `NETWORK_TOOLS`, `JOBS_TOOLS` (incluindo a leitura de apoio `list_contacts` e `network_company_overview`), `APPROVAL_TOOLS`, `DASHBOARD_TOOLS`, conforme a tabela do plano.
3. `agent_tools(agent)`: abre o `MCPAdapter`, `list_tools()`, devolve só as ferramentas da lista; ferramenta anunciada e não classificada gera erro. Um contexto aberto por turno.
4. `call(tool, **args)`: chamada direta pelo `fastmcp.Client`, devolvendo o conteúdo estruturado.
5. `extract_proposal(tool_message)`: lê `artifact["structured_content"]` (ou o equivalente confirmado na versão instalada) e reconhece `{"proposal": {...}}`.
6. Medir o tempo de partida do servidor e anotar (risco aceito do plano).

## Critérios de conclusão

- [ ] Teste de integração: os nomes entregues a Network e a Vagas são exatamente os da tabela do plano; Vagas recebe `list_contacts` e `network_company_overview` e nenhuma escrita de Network; nenhum agente recebe `changes_*`.
- [ ] Teste: as 17 ferramentas anunciadas estão todas classificadas.
- [ ] Teste: `add_job` chamado direto devolve proposta e o banco não muda até `changes_confirm`.
- [ ] Teste: a variável `OPENAI_API_KEY` não é repassada ao processo do servidor.
- [ ] Tempo de partida do servidor anotado na validação.

## Validação

A preencher: comandos, contagem de testes, tempo de partida, observações sobre a API beta de `langchain.mcp` na versão fixada.

## Status

```text
pendente
```
