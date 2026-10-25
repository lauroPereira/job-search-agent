# job-search-agent

Aplicação local com **chat** e **dashboards** em que agentes de IA ajudam a gerir uma busca de emprego. Toda leitura e gravação de dados passa pelo servidor MCP [job-search-mcp](https://github.com/lauroPereira/job-search-mcp), com aprovação humana antes de qualquer alteração.

> **Estado:** base do projeto criada a partir do [ai-dev-template](https://github.com/lauroPereira/ai-dev-template) `v0.3.0`. Especificação e decisões em preparação; ainda não há código.

## Por que este projeto existe

O [job-search-mcp](https://github.com/lauroPereira/job-search-mcp) oferece as ferramentas e os dados, sem modelo de linguagem. Este repositório é o outro lado: o agente que usa essas ferramentas. Ele demonstra, num caso real e pequeno:

- **orquestração multiagente:** um supervisor e agentes por domínio, cada um só com as ferramentas do seu domínio;
- **guardrails e harness:** aprovação humana antes de gravar, nada é enviado em nome da pessoa, limite de tokens por turno;
- **conhecimento e RAG:** busca semântica local, com a fonte citada;
- **avaliação:** casos de referência versionados, rodando no CI sem chave de API;
- **observabilidade e relatórios:** passos, ferramentas, tokens e custo de cada conversa; dashboards calculados sem modelo.

## Tecnologia (decidida)

Python 3.12, Streamlit, LangGraph e LangChain, modelos da API da OpenAI e base vetorial local. As versões e bibliotecas são fixadas no plano técnico.

## Como o projeto é desenvolvido

Desenvolvimento guiado por especificação (SDD), com agentes em papéis definidos (Supervisor, Developer, Reviewer e QA):

```text
especificação → plano → tarefas → implementação → validação
```

- Especificações e plano: [`docs/specs/`](docs/specs/)
- Tarefas: [`docs/tasks/`](docs/tasks/)
- Decisões: [`docs/architecture/decisions/`](docs/architecture/decisions/)
- Evidências: [`docs/evidence/`](docs/evidence/)
- Estágios: `develop` (dev) → `main` (hml) → tag `v*.*.*` (prd); tudo entra por pull request
- Instruções para agentes: [`AGENTS.md`](AGENTS.md) e [`CLAUDE.md`](CLAUDE.md)
- Origem e versão do template: [`docs/wiki/origem-template.md`](docs/wiki/origem-template.md)

## Como validar

```powershell
.\tools\scripts\validate-project.ps1
.\tools\scripts\validate-agent-flow.ps1
```

Quando houver código Python: `python tools/scripts/lint_and_tests.py --strict` (o mesmo comando do CI).

## Dados e privacidade

O repositório é público e **não contém dados reais**. Dados de demonstração, documentos da base de conhecimento e casos de avaliação são sintéticos. Banco, base vetorial, rastros e chaves de API ficam na máquina de quem usa, fora do Git.

## Licença

[MIT](LICENSE).
