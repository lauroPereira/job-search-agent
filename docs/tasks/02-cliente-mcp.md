# Tarefa: cliente MCP e ferramentas por agente

## Objetivo

Conectar o agente ao servidor job-search-mcp por stdio com `langchain.mcp`, entregar a cada agente só a sua lista de ferramentas e oferecer chamadas diretas (sem modelo) para aprovação e dashboard.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Cliente MCP" e "Grafo" (tabela de ferramentas). Critério da especificação: "Teste: cada agente só vê as ferramentas do seu domínio".

## Pré-condições

Tarefa 01 concluída. Q3 (leitura entre domínios) respondida ou a proposta do plano aceita.

## Arquivos prováveis

`src/job_search_agent/mcp_client.py`, `tests/conftest.py` (fixture do servidor com seed em pasta temporária), `tests/test_mcp_client.py`.

## Passos

1. Fixture de teste: banco temporário com caminho absoluto, `job-search-mcp --seed`, servidor iniciado por `StdioTransport` com só `JOB_SEARCH_DB` (e `JOB_SEARCH_CONFIG`, se houver) em `env`.
2. `mcp_client.py`: abrir o `MCPAdapter`, `list_tools()`, e as constantes `NETWORK_TOOLS`, `JOBS_TOOLS`, `APPROVAL_TOOLS`, `DASHBOARD_TOOLS` conforme o plano.
3. `tools_for(agent)` devolve só as ferramentas da lista; ferramenta anunciada e não classificada gera erro.
4. `call(tool, **args)` para chamadas diretas, devolvendo o conteúdo estruturado (`artifact["structured_content"]` ou equivalente confirmado na versão instalada).
5. `extract_proposal(tool_message)` reconhece `{"proposal": {...}}`.

## Critérios de conclusão

- [ ] Teste de integração: os nomes entregues a Network e a Vagas são exatamente os da tabela do plano; nenhum agente recebe `changes_*`.
- [ ] Teste: as 17 ferramentas anunciadas estão todas classificadas.
- [ ] Teste: `add_job` chamado direto devolve proposta e o banco não muda até `changes_confirm`.
- [ ] Teste: a variável `OPENAI_API_KEY` não é repassada ao processo do servidor.

## Validação

A preencher: comandos, contagem de testes, observações sobre a API beta de `langchain.mcp` na versão fixada.

## Status

```text
pendente
```
