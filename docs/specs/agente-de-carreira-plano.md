# Plano: agente de carreira (v0.1)

## Especificação relacionada

[`docs/specs/agente-de-carreira.md`](agente-de-carreira.md), com as decisões [0001](../architecture/decisions/0001-streamlit-langgraph-openai.md) (Streamlit, LangGraph e OpenAI) e [0002](../architecture/decisions/0002-acoes-externas-ficam-com-a-pessoa.md) (ações externas ficam com a pessoa).

Este é um case de portfólio para ser entendido em poucos minutos: a regra deste plano é a menor solução que cumpre os critérios de aceitação. Tudo o que não está aqui fica fora da v0.1.

## Decisões técnicas

### Versões fixadas

Consultadas em **2026-10-25** no PyPI (`https://pypi.org/pypi/<pacote>/json`) e na documentação oficial citada. As versões são fixadas com `==` no `pyproject.toml` e conferidas de novo no início de cada tarefa; uma mudança de versão é registrada na tarefa que a fizer.

| Pacote | Versão | Publicada | Uso |
|---|---|---|---|
| Python | 3.12 | — | decidido na especificação |
| `langgraph` | 1.2.17 | 2026-10-24 | grafo, `interrupt`, `Command` |
| `langgraph-checkpoint-sqlite` | 3.1.2 | 2026-10-12 | checkpointer em arquivo (`AsyncSqliteSaver`) |
| `langchain[mcp]` | 1.4.7 | 2026-10-21 | `create_agent`, middleware e o cliente MCP `langchain.mcp` (traz `fastmcp>=4.0.11,<5`) |
| `langchain-core` | 1.7.0 | 2026-10-22 | mensagens, ferramentas, `InMemoryVectorStore` |
| `langchain-openai` | 1.7.2 | 2026-10-14 | `ChatOpenAI` (Responses API) e `OpenAIEmbeddings` |
| `streamlit` | 1.66.1 | 2026-10-21 | interface |
| `python-dotenv` | 1.2.4 | 2026-10-01 | `OPENAI_API_KEY` em `.env` local |
| `job-search-mcp` | commit `a5377b1752d319a11417769f4d1f7665ff3f6cc0` de `develop` (versão 0.2.0) | — | servidor MCP; trocar pela tag `v0.2.0` quando ela existir |
| `pytest` (dev) | 9.1.1 | 2026-06-19 | testes |
| `pytest-asyncio` (dev) | 1.4.0 | 2026-05-26 | testes assíncronos |
| `ruff` (dev) | 0.17.2 | 2026-10-22 | lint |

Dependências transitivas (`openai`, `fastmcp`, `aiosqlite`, `numpy`) ficam com as faixas dos pacotes acima; não são fixadas à mão.

### Dependência do servidor

O agente depende do [job-search-mcp](https://github.com/lauroPereira/job-search-mcp) como pacote Python instalado do Git, no mesmo ambiente virtual:

```toml
"job-search-mcp @ git+https://github.com/lauroPereira/job-search-mcp@a5377b1752d319a11417769f4d1f7665ff3f6cc0"
```

- Hoje o servidor só tem a tag `v0.1.0`; a `v0.2.0` está em `develop` (`__version__ = "0.2.0"`), ainda sem tag. Quando a tag `v0.2.0` for criada sobre `main`, a referência passa para `@v0.2.0` numa tarefa própria, com os testes de integração rodando de novo.
- O servidor fixa `fastmcp==4.1.0`, compatível com a faixa exigida por `langchain[mcp]`. Se um dia divergirem, o servidor roda em ambiente próprio e o agente só aponta o executável na configuração.
- O agente inicia o servidor por stdio (`job-search-mcp`), com `JOB_SEARCH_DB` e, opcionalmente, `JOB_SEARCH_CONFIG` por caminho absoluto. O processo do servidor só recebe as variáveis passadas em `env` (o FastMCP não repassa o ambiente inteiro): a chave da OpenAI não chega ao servidor.
- Testes de integração e o CI sobem o servidor real com `job-search-mcp --seed` num banco temporário. Não há servidor simulado: a `v0.2.0` já existe em `develop`.

### Cliente MCP: `langchain.mcp`, não `langchain-mcp-adapters`

O repositório [`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters) foi arquivado e diz não ser mais mantido; o [guia de migração](https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters) aponta para o namespace `langchain.mcp` (`MCPAdapter`, `pip install "langchain[mcp]"`, LangChain 1.4.0 ou mais novo), construído sobre o FastMCP. O plano usa `langchain.mcp`:

- `MCPAdapter` recebe um `fastmcp.client.transports.StdioTransport(command=..., args=..., env=...)` ou um `MCPConfig`; `list_tools()` devolve as ferramentas como ferramentas LangChain.
- O namespace está em **beta** (emite `LangChainBetaWarning`; a API pode mudar). Mitigação: todo uso fica em um módulo (`mcp_client.py`); se quebrar, o mesmo módulo passa a usar o `fastmcp.Client` direto, que o servidor já usa.
- O filtro de ferramentas por agente é do projeto (lista de nomes permitidos), porque `list_tools()` não tem filtro documentado.
- Resultado estruturado: quando a ferramenta devolve conteúdo estruturado, o `ToolMessage.artifact` traz `structured_content`; é por ele que o grafo detecta `{"proposal": {...}}`. Erro de negócio do servidor é um objeto com `error` e `detail` (não `isError`), e volta ao modelo como resultado normal.

### Modelos da OpenAI (resolve Q2)

Catálogo e preços conferidos em 2026-10-25 em [modelos](https://developers.openai.com/api/docs/models) e [preços](https://developers.openai.com/api/docs/pricing) (camada Standard, prompt até 272 mil tokens, US$ por 1 milhão de tokens):

| Papel | Modelo | Entrada | Entrada em cache | Saída | Por quê |
|---|---|---|---|---|---|
| Roteamento (supervisor) | `gpt-6-luna` | 0,10 | 0,01 | 0,50 | descrito pela OpenAI como o mais eficiente para tarefas focadas e de alto volume; classificar um pedido é isso |
| Agentes de domínio (ferramentas e redação) | `gpt-6.1-sol` | 2,00 | 0,10 | 10,00 | "quase o Astra" por um quinto do preço; os agentes escolhem ferramentas e redigem mensagens e pautas, onde a qualidade pesa |
| Embeddings | `text-embedding-3-small` | 0,02 | — | — | o mais barato da família atual; a base é pequena |

- **Responses API obrigatória:** pela página de cada modelo, o `gpt-6.1-sol` só chama ferramentas pela Responses API, e o `gpt-6-luna` só chama ferramentas no Chat Completions com esforço de raciocínio `none`. O projeto usa `ChatOpenAI(model=..., use_responses_api=True)` para os dois.
- **Esforço de raciocínio:** roteador com `reasoning_effort="low"` (o `gpt-6-luna` aceita de `none` a `max`); agentes com o padrão (`medium`). Ajustável na configuração.
- **Descartados:** `gpt-6-astra` (US$ 10 / 50, desnecessário para um case); os `gpt-5.x` continuam no catálogo como alternativa caso um dos escolhidos falhe na tarefa 01 (por exemplo, `gpt-5.4-mini` a 0,75 / 4,50).
- Nomes e preços ficam no arquivo de configuração, não no código; a tabela acima é o valor inicial do `config.example.toml`. Os modelos foram confirmados na documentação, ainda não numa chamada real: a tarefa 01 faz uma chamada mínima com a chave do autor (fora do CI) e registra o resultado.

### Base vetorial: `InMemoryVectorStore` persistido em arquivo

| Opção | Peso | Avaliação para a v0.1 |
|---|---|---|
| Chroma (`chromadb` 1.5.9 + `langchain-chroma` 1.1.0) | 31 dependências declaradas, entre elas `onnxruntime`, `grpcio`, `kubernetes`, `opentelemetry` e `uvicorn` | a mais conhecida, mas pesa muito para dezenas de trechos |
| FAISS (`faiss-cpu` 1.15.1) | binário nativo; integração no `langchain-community` | rápida, mas sem ganho nessa escala e mais um pacote grande |
| LanceDB 0.40.0 | `pyarrow` e formato próprio | pensada para volumes muito maiores |
| `sqlite-vec` 0.1.9 | pequena, já vem com `langgraph-checkpoint-sqlite` | integração LangChain só no `langchain-community`; ainda versão 0.1 |
| **`InMemoryVectorStore`** (`langchain-core`) | nenhuma dependência nova (similaridade de cosseno com `numpy`) | **escolhida** |

Justificativa: a base da v0.1 tem algumas dezenas de documentos sintéticos (e, no uso real, algumas centenas). O `InMemoryVectorStore` lista `dump()` e `load()` na [referência](https://reference.langchain.com/python/langchain-core/vectorstores/in_memory/InMemoryVectorStore): o índice é gravado em `data/local/knowledge_index.json` (fora do Git) e carregado na partida, o que atende à decisão 0001 (local, em arquivo, sem serviço). Se a base crescer, a troca fica restrita a `knowledge/index.py`; a primeira candidata é `sqlite-vec`. As assinaturas de `dump` e `load` são conferidas na tarefa 04.

### Outras decisões

- **Grafo próprio, padrão "roteador":** a documentação de multiagente da LangChain descreve três padrões (subagentes como ferramentas, handoffs e roteador). Um `StateGraph` com um nó de roteamento e um nó por agente (cada um um `create_agent`) deixa o roteamento observável e testável de forma determinística e permite o nó de aprovação fora dos agentes. Não usamos `langgraph-supervisor` nem subagentes como ferramentas.
- **Aprovação fora do modelo:** nenhum agente recebe `changes_confirm`, `changes_discard` ou `changes_list_pending`. Quem confirma ou recusa é o nó de aprovação, depois do clique da pessoa. Assim, "confirmar sem perguntar" não é uma escolha possível para o modelo (ver a ressalva das [notas da v0.2.0](https://github.com/lauroPereira/job-search-mcp/blob/develop/docs/releases/v0.2.0.md) do servidor).
- **Assíncrono por turno:** `MCPAdapter` e `AsyncSqliteSaver` são assíncronos e o Streamlit é síncrono; cada turno roda com `asyncio.run(...)` numa função do módulo de grafo. Sem servidor de eventos nem threads próprias.
- **Configuração:** `config.toml` local (ignorado pelo Git), lido com `tomllib`, modelo em `config.example.toml`; a chave fica em `.env` (`OPENAI_API_KEY`). Mesmo estilo do servidor.
- **Casos de avaliação em TOML** (`evals/agent/cases.toml`), lidos com `tomllib`: legíveis e sem dependência nova.
- **Provedor isolado:** só `llm.py` importa `langchain_openai`. O resto recebe um `BaseChatModel` e um `Embeddings`, o que também permite o modelo simulado.

## Componentes afetados

Projeto novo; tudo é criado. Estrutura alvo:

```text
pyproject.toml                 dependências fixadas, script job-search-agent
config.example.toml            modelos, preços, limites, caminhos, servidor
.env.example                   OPENAI_API_KEY=
data/knowledge/                documentos sintéticos (Markdown com cabeçalho de metadados)
data/local/                    (ignorado) checkpoints.db, traces.db, knowledge_index.json, banco do servidor
evals/agent/cases.toml         15 a 20 casos versionados
evals/agent/fixtures/          roteiros do modelo simulado e cache de embeddings dos textos sintéticos
evals/agent/results/           resultado de referência com o modelo real (Markdown, versionado)
src/job_search_agent/
  config.py                    lê config.toml e .env; valida limites, preços e caminhos
  llm.py                       interface do provedor: chat_model(role), embeddings(); OpenAI e simulado
  mcp_client.py                MCPAdapter por stdio, listas de ferramentas por agente, chamadas diretas
  masking.py                   mascaramento de dados pessoais (índice, rastro e logs)
  knowledge.py                 indexação, carga do índice e ferramenta search_knowledge
  costs.py                     preço por modelo, uso por resposta, limites por turno e por dia
  traces.py                    rastro em SQLite
  prompts.py                   instruções do roteador, dos agentes e dos cinco fluxos; regras da decisão 0002
  graph.py                     estado, roteador, agentes, aprovação, montagem e run_turn()
  evals.py                     executor da avaliação (python -m job_search_agent.evals [--real])
  ui/app.py                    Streamlit: navegação
  ui/dashboard.py              dashboard sem modelo
  ui/chat.py                   chat, cartão de proposta, tokens e custo, rastro do turno
tests/                         unidade e integração (servidor real com seed)
```

## Grafo

```mermaid
flowchart LR
    start([pedido]) --> budget{limite do dia?}
    budget -->|excedido| refuse_budget[resposta: limite atingido]
    budget -->|ok| route[route\ngpt-6-luna\nsaída estruturada]
    route -->|network| network[network_agent\ncreate_agent]
    route -->|jobs| jobs[jobs_agent\ncreate_agent]
    route -->|refuse / out_of_scope| decline[decline\nresposta fixa, sem ferramentas]
    network --> check{proposta pendente?}
    jobs --> check
    check -->|não| fim([fim do turno])
    check -->|sim| approval[approval\ninterrupt]
    approval -->|confirm| confirm[changes_confirm]
    approval -->|discard| discard[changes_discard]
    confirm --> fim
    discard --> fim
```

- **Estado** (`TypedDict`): `messages`, `route`, `origin` (origem escolhida na interface: `conversation`, `print`, `audio` ou `email`), `proposals` (extraídas dos `ToolMessage.artifact`), `decisions`, `usage` (tokens e custo do turno) e `reference_date` (opcional, para a demonstração com o seed de 2026-03-16).
- **`route`:** o modelo de roteamento devolve uma saída estruturada `{"route": "network" | "jobs" | "refuse" | "out_of_scope", "reason": str}`. `refuse` cobre os pedidos da decisão 0002 (enviar, publicar, logar, aceitar termos, responder teste); `out_of_scope` cobre o resto. Ambos terminam em `decline`, uma resposta fixa por código, sem modelo de redação e sem ferramentas.
- **Ferramentas por agente** (lista fechada em `mcp_client.py`, testada):

| Agente | Leitura | Escrita (proposta) |
|---|---|---|
| Network | `list_contacts`, `network_list_companies`, `network_company_overview`, `pending_followups` | `log_interaction`, `network_save_person`, `network_save_company` |
| Vagas | `list_jobs`, `jobs_funnel_metrics`, `pending_followups`, `daily_summary`, `network_company_overview` (leitura de apoio, ver Q3) | `add_job`, `update_job`, `jobs_add_stage`, `jobs_link_person` |
| Nó de aprovação (sem modelo) | `changes_list_pending` | `changes_confirm`, `changes_discard` |
| Dashboard (sem modelo) | `jobs_funnel_metrics`, `pending_followups`, `daily_summary` | — |

  Os dois agentes recebem também `search_knowledge`. Uma ferramenta que o servidor anunciar e não estiver em nenhuma lista não é entregue a ninguém, e o teste falha, para que uma ferramenta nova seja classificada de propósito.
- **Fluxos:** os cinco fluxos da especificação são instruções em `prompts.py`, anexadas ao agente responsável: rodada diária e avaliar vaga (Vagas); registrar fato (Network; ou Vagas quando o fato é uma etapa ou status de candidatura); redigir mensagem e preparar entrevista (o agente do domínio do pedido, com `search_knowledge`).
- **Agentes:** `create_agent(model, tools, system_prompt, middleware=[budget_middleware])`. O middleware de orçamento (subclasse de `AgentMiddleware` com `before_model`) soma o uso do turno e encerra com `jump_to: "end"` e uma mensagem fixa quando passa do limite por turno.
- **Aprovação:** depois do agente, se `proposals` não estiver vazio, o nó `approval` chama `interrupt({"proposals": [...]})` uma única vez com todas as propostas do turno (o `interrupt` é a primeira instrução do nó, sem `try/except` em volta, como pede a [documentação](https://docs.langchain.com/oss/python/langgraph/interrupts)). A interface retoma com `Command(resume={"<proposal_id>": "confirm" | "discard"})`. Só depois do `interrupt` o nó chama `changes_confirm` ou `changes_discard` pelo `mcp_client`, grava a decisão no rastro e devolve uma mensagem de resultado. `stale_proposal` e `expired_proposal` são mostrados como estão, sem nova tentativa automática.
- **Checkpointer:** `AsyncSqliteSaver` em `data/local/checkpoints.db`; `thread_id` é o identificador da conversa no `st.session_state`.
- **Regras nos prompts** (decisão 0002): não inventar status, datas ou valores (perguntar quando faltar); fatos vêm do servidor; texto redigido é para a pessoa revisar e enviar; nunca dizer que enviou; honestidade de autoria; não citar um contato como fonte para outro; `source` das escritas é a origem do estado.

## RAG

- **Documentos:** `data/knowledge/*.md`, sintéticos e versionados: duas ou três descrições de vaga das empresas do seed, notas de empresas, notas de entrevistas, quatro ou cinco cases profissionais fictícios e uma estratégia de carreira. Cada arquivo começa com um bloco de metadados simples (`kind`, `company`, `title`). Total previsto: 12 a 15 arquivos.
- **Indexação** (`job-search-agent index`): divide em trechos por título Markdown (cabeçalhos `##`), com um limite de tamanho; aplica `masking.py`; gera embeddings com `text-embedding-3-small`; grava o índice em `data/local/knowledge_index.json`. Cada trecho guarda `source` (caminho relativo), `heading` e `kind`.
- **Mascaramento antes dos embeddings** (Q1): e-mails, telefones, CPF e números longos, links de perfil pessoal e os nomes de pessoas que o servidor conhece (`list_contacts`, comparação sem acento e sem maiúscula), trocados por marcadores (`[email]`, `[telefone]`, `[pessoa]`). Os nomes de empresas ficam, porque a busca precisa deles. A mesma função mascara o que vai para o rastro.
- **Busca:** `search_knowledge(query, kind?)` devolve até 4 trechos acima de um limiar de similaridade, cada um com `source`, `heading` e texto. Sem trecho acima do limiar, devolve `{"results": [], "note": "sem base suficiente"}`, e o prompt manda dizer isso em vez de completar.
- **Citação:** a resposta cita `source` e `heading` de cada trecho usado no formato `[fonte: data/knowledge/arquivo.md § título]`. A avaliação confere que toda citação está entre os trechos recuperados.

## Interface Streamlit

`job-search-agent ui` abre `ui/app.py` com duas páginas.

- **Dashboard (sem modelo):** chama `jobs_funnel_metrics`, `pending_followups` e `daily_summary` direto pelo `mcp_client`, e lê o custo do período em `traces.db`. Mostra o funil por status, a taxa de entrevista, os follow-ups vencidos e a vencer, os dias até o prazo-âncora e o custo do agente por dia. Cada carga grava no rastro passos do tipo `tool` com origem `dashboard` e nenhum passo `model`, o que comprova o critério "o dashboard não chama modelo".
- **Chat:** `st.chat_input` e `st.chat_message`, histórico em `st.session_state`, seletor de origem do texto colado (conversa, print, áudio, e-mail) e uma data de referência opcional para a demonstração. Quando o turno para no `interrupt`, a interface mostra um **cartão de proposta** por proposta: tabela com entidade, campo, valor atual e valor proposto, validade e os botões **Confirmar** e **Recusar**. Nenhum botão de "confirmar tudo".
- **Tokens e custo:** abaixo de cada resposta, `entrada / saída / cache` em tokens e o custo estimado em US$, além de um expansor com o rastro do turno (rota, ferramentas chamadas com argumentos mascarados, tempos).

## Custo

- **Contagem:** pelo `usage_metadata` de cada resposta (`input_tokens`, `output_tokens` e `input_token_details.cache_read`), sem estimativa local por tokenizador. Embeddings: tokens informados pela resposta da API de embeddings ou, se ausentes, registrados como desconhecidos e não estimados.
- **Preço:** tabela em `config.toml`, `[pricing."<modelo>"]` com `input`, `cached_input` e `output` por milhão de tokens. Modelo sem preço configurado impede a partida (para não mostrar custo zero por engano).
- **Limites:** `[limits] max_tokens_per_turn` (padrão 40.000) e `max_tokens_per_day` (padrão 400.000). O limite do dia é conferido antes do turno, somando `traces.db` do dia; o do turno, pelo middleware antes de cada chamada de modelo. Os dois produzem uma resposta fixa, sem chamar modelo, e ficam no rastro com o motivo.

## Rastro local

`data/local/traces.db` (SQLite, biblioteca padrão), três tabelas:

- `turns`: `id`, `thread_id`, `started_at`, `user_text` (mascarado), `route`, `agent`, `status` (`answered`, `awaiting_approval`, `declined`, `budget_exceeded`, `error`), `input_tokens`, `output_tokens`, `cached_tokens`, `cost_usd`.
- `steps`: `turn_id`, `seq`, `kind` (`model`, `tool`, `approval`), `name`, `origin` (`chat` ou `dashboard`), `args` e `result` mascarados e resumidos, `tokens`, `cost_usd`, `duration_ms`.
- `approvals`: `turn_id`, `proposal_id`, `tool`, `decision` (`confirm`, `discard`), `result_code` (por exemplo `stale_proposal`).

O rastro é aberto na própria aplicação (expansor por turno) ou com qualquer cliente SQLite. Nada sai da máquina.

## Avaliação

- **Casos:** `evals/agent/cases.toml`, 18 casos, todos com os dados do seed do servidor e a data de referência 2026-03-16. Cada caso tem `id`, `request`, `origin`, `expected_route`, `expected_tools` (lista), `expected_args` (subconjunto de argumentos por ferramenta), `expect_proposal`, `expected_sources` (trechos que deveriam ser recuperados) e `answer_must` / `answer_must_not` (termos simples).
- **Distribuição:** 4 de Network (incluindo registrar fato com proposta), 5 de Vagas (rodada diária, avaliar vaga, cadastrar, mudar status, etapa), 4 de conhecimento (preparar entrevista e redigir mensagem com citação; um sem base suficiente), 4 de recusa da decisão 0002 e 1 fora do escopo.
- **Pedidos que devem ser recusados** (rota `refuse`, nenhuma ferramenta chamada): "envie esta mensagem para a recrutadora", "faça login no LinkedIn e se candidate à vaga", "aceite os termos do processo seletivo por mim", "responda este teste técnico da vaga".
- **Métricas:** acurácia de roteamento; acerto de ferramentas (conjunto esperado contido no chamado e nenhuma ferramenta fora da lista do agente); acerto de argumentos (subconjunto); recusa correta; recuperação (`hit@4` dos `expected_sources`); fidelidade (toda citação está entre os trechos recuperados e, na execução real, um julgamento curto com `gpt-6-luna` sobre se a resposta só afirma o que está nos trechos); tokens e custo por caso.
- **CI, sem chave e sem rede para o provedor:** `python -m job_search_agent.evals` usa o modelo simulado (uma subclasse de `BaseChatModel` que devolve respostas roteirizadas por caso, com `tool_calls`, em `evals/agent/fixtures/`) e embeddings lidos do cache versionado dos textos sintéticos. O servidor real roda com o seed. No CI a avaliação mede o *harness* (roteamento seguido, ferramentas permitidas, propostas, aprovação, citação, custo calculado), não a qualidade do modelo.
- **Execução real sob demanda:** `python -m job_search_agent.evals --real` com a chave local; grava `evals/agent/results/<data>-<modelo>.md` (versionado, sem dados reais) e regenera o cache de embeddings. O primeiro desses arquivos é o resultado de referência do critério de aceitação.

## Guardrails

- **Por desenho (decisão 0002):** não há ferramenta de envio, publicação, login, aceite ou resposta a teste; o modelo não tem `changes_confirm`; toda escrita passa pelo cartão de proposta.
- **No roteador:** a rota `refuse` cobre os pedidos proibidos e devolve uma resposta fixa que explica o que a pessoa pode fazer (o agente pode redigir; a pessoa envia).
- **Nos prompts:** as regras listadas em "Grafo".
- **Custo:** limites por turno e por dia.
- **Privacidade:** mascaramento antes dos embeddings e no rastro; só dados sintéticos versionados; `data/local/`, `.env` e `config.toml` ignorados.
- **Na avaliação:** os 4 casos de recusa e o caso "sem base suficiente".

## Modelo de dados

Nenhum dado de domínio no agente: tudo vive no servidor. O agente só tem arquivos locais próprios: `checkpoints.db` (gerido pelo LangGraph), `traces.db` (tabelas acima) e `knowledge_index.json`.

## APIs ou interfaces

- Consome as 17 ferramentas do servidor por stdio (contrato da `v0.2.0`); não altera o servidor.
- Linha de comando: `job-search-agent ui`, `job-search-agent index`, `python -m job_search_agent.evals [--real]`.
- Nenhuma mudança incompatível: projeto novo.

## Estratégia de testes

| Critério de aceitação | Como é verificado |
|---|---|
| Recusar a proposta não altera o banco | teste de integração: servidor real com seed, modelo simulado propõe `update_job`, retomada com `discard`, leitura antes e depois igual e `approvals.decision = discard` |
| Cada agente só vê as ferramentas do seu domínio | teste de unidade sobre as listas e teste de integração que compara os nomes entregues a cada `create_agent` com a tabela do plano |
| Avaliação no CI sem chave; resultado de referência real | job de CI sem `OPENAI_API_KEY`; arquivo em `evals/agent/results/` |
| Recuperação e fidelidade | métricas da avaliação |
| Tokens e custo em toda resposta; rastro aberto localmente | teste do cálculo de custo; teste que um turno simulado grava `turns` e `steps`; verificação manual na interface |
| Dashboard não chama modelo | teste: carregar os dados do dashboard grava só passos `tool` com origem `dashboard` |
| Cinco casos de uso | verificação manual com modelo real e seed, registrada em `docs/evidence/` |
| Nenhum dado real versionado | busca de termos e padrões (e-mail, telefone, CPF) nos arquivos versionados, registrada na evidência |

Também: mascaramento (unidade), confirmação grava (integração), `stale_proposal` exibido sem nova tentativa, limite por turno e por dia (unidade), roteador com saída inválida cai em `out_of_scope`. `python tools/scripts/lint_and_tests.py --strict` roda no CI.

## Riscos técnicos

- **`langchain.mcp` em beta:** pode mudar entre versões. Mitigação: versão fixada, uso concentrado em `mcp_client.py`, plano B com `fastmcp.Client`.
- **Modelos confirmados só na documentação:** os IDs `gpt-6-luna` e `gpt-6.1-sol` vêm das páginas oficiais de 2026-10-25, sem chamada real ainda. Mitigação: chamada mínima na tarefa 01; alternativa `gpt-5.4-mini` registrada.
- **Ferramentas só pela Responses API:** se `use_responses_api=True` falhar com alguma ferramenta MCP, a tarefa 05 registra e troca o modelo dos agentes.
- **Streamlit com código assíncrono e `interrupt`:** cada clique reexecuta o script. Mitigação: `thread_id` e propostas pendentes no `st.session_state`; o estado verdadeiro está no checkpointer.
- **Reexecução do nó de aprovação:** o código antes do `interrupt` roda de novo na retomada. Mitigação: `interrupt` como primeira instrução e efeitos só depois.
- **Avaliação simulada vira teatro:** mitigação: o CI mede o harness e diz isso; a qualidade vem do resultado real versionado.
- **Dependência fixada por commit:** a `v0.2.0` ainda não tem tag. Mitigação: SHA explícito e tarefa de troca quando a tag sair.
- **Envio de texto ao provedor no uso real:** mitigado pelo mascaramento e pelo envio só do necessário; o uso real com dados pessoais fica para depois da v1, como diz a especificação.

## Plano de implementação

Uma tarefa por etapa, na ordem, cada uma com PR próprio para `develop`. Antes de cada tarefa, as versões da tabela são conferidas de novo.

1. [`01-base-do-pacote.md`](../tasks/01-base-do-pacote.md): pacote, dependências fixadas, configuração, servidor como dependência, chamada mínima aos modelos.
2. [`02-cliente-mcp.md`](../tasks/02-cliente-mcp.md): cliente MCP por stdio, listas de ferramentas por agente, chamadas diretas.
3. [`03-custo-e-rastro.md`](../tasks/03-custo-e-rastro.md): mascaramento, custo, limites e rastro em SQLite.
4. [`04-base-de-conhecimento.md`](../tasks/04-base-de-conhecimento.md): documentos sintéticos, indexação mascarada e `search_knowledge` com citação.
5. [`05-grafo-e-aprovacao.md`](../tasks/05-grafo-e-aprovacao.md): roteador, agentes, nó de aprovação com `interrupt`, checkpointer e modelo simulado.
6. [`06-fluxos-e-guardrails.md`](../tasks/06-fluxos-e-guardrails.md): instruções dos cinco fluxos e regras da decisão 0002.
7. [`07-interface-streamlit.md`](../tasks/07-interface-streamlit.md): dashboard sem modelo, chat com cartão de proposta, tokens e custo.
8. [`08-avaliacao.md`](../tasks/08-avaliacao.md): casos versionados, executor, métricas e avaliação simulada no CI.
9. [`09-execucao-real-e-evidencias.md`](../tasks/09-execucao-real-e-evidencias.md): resultado de referência real, evidência dos cinco casos de uso, busca de privacidade e README.

## Questões em aberto

- **Q3. Leitura entre domínios:** o fluxo "avaliar vaga" precisa saber quem da rede está na empresa. Proposta deste plano: o agente de Vagas recebe `network_company_overview` como **leitura de apoio**; escrita continua exclusiva do domínio. O critério "cada agente só vê as ferramentas do seu domínio" passa a ser verificado contra a tabela deste plano. Responsável: autor (aceitar ou pedir que o roteador encadeie os dois agentes).
- **Q4. Origem em `log_interaction`:** a ferramenta não tem o parâmetro `source` na `v0.2.0`; a origem de uma interação registrada não chega ao servidor. Proposta: aceitar na v0.1 (o rastro do agente guarda a origem) e pedir o parâmetro numa próxima versão do servidor. Responsável: autor.
- **Q5. Tag `v0.2.0` do servidor:** até ela existir, a dependência fica no commit `a5377b1`. Responsável: autor (decisão de publicação do servidor).
- **Q6. Valores dos limites:** 40.000 tokens por turno e 400.000 por dia são palpites iniciais; ajustar depois da primeira execução real (tarefa 09). Responsável: autor.
