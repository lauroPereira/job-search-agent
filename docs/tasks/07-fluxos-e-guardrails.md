# Tarefa: fluxos e guardrails

## Objetivo

Escrever as instruções do roteador, dos agentes e dos cinco fluxos (rodada diária, registrar fato, avaliar vaga, redigir mensagem, preparar entrevista), com as regras da decisão 0002, a pergunta quando faltar dado e a citação de fonte.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Grafo" (fluxos e regras) e "Guardrails"; [decisão 0002](../architecture/decisions/0002-acoes-externas-ficam-com-a-pessoa.md). Casos de uso 1 a 5 da especificação; requisito "quando faltar dado, pergunta".

## Pré-condições

Tarefas 05 e 06 concluídas.

## Arquivos prováveis

`src/job_search_agent/prompts.py`, `tests/test_prompts.py`.

## Passos

1. Instruções do roteador com exemplos de cada rota, inclusive os quatro pedidos de recusa do plano.
2. Instruções comuns: não inventar status, datas ou valores; quando faltar dado, perguntar e não propor; fatos do servidor; texto redigido é para a pessoa enviar; nunca dizer que enviou; honestidade de autoria; discrição entre contatos; `source` = origem do estado; data de referência; formato de citação.
3. Instruções de cada fluxo, anexadas ao agente responsável; rodada diária com no máximo cinco ações e sem escrita; avaliar vaga usando a leitura de apoio (`list_contacts` com `company`).
4. Respostas fixas de `decline` (recusa com o que a pessoa pode fazer; fora do escopo).

## Critérios de conclusão

- [x] Teste: cada regra da decisão 0002 e a regra "perguntar quando faltar dado" aparecem nas instruções comuns dos dois agentes.
- [x] Teste: as respostas de `decline` não prometem envio nem ação externa.
- [ ] Verificação manual curta com modelo real (fora do CI) de um caso de cada fluxo e de um pedido com dado faltante, anotada aqui; a evidência formal fica na tarefa 10.

## Validação

Executada em 2026-10-26, Windows 11, `.venv` com Python 3.12 (versões da tarefa 01, sem mudança). Sem chave da OpenAI: os critérios automáticos foram verificados com o modelo simulado e o servidor real sobre `data/demo/`; a verificação manual com modelo real está **pendente** (ver "Pendências").

**Instruções** (`src/job_search_agent/prompts.py`)

- Roteador: as quatro rotas com exemplos, os quatro pedidos de recusa do plano (um por linha) e a regra "redigir um texto para a pessoa enviar não é refuse".
- `COMMON` (dado aos dois agentes), regras numeradas:
  1. fatos do servidor, não da memória; não inventar status, datas ou valores;
  2. faltando dado para gravar, perguntar e não propor;
  3. toda gravação é proposta confirmada pela pessoa;
  4. não enviar, publicar, fazer login, se candidatar, aceitar termos nem responder testes; texto redigido é para a pessoa enviar; nunca dizer que enviou;
  5. honestidade de autoria;
  6. discrição entre contatos;
  7. `search_knowledge` com citação no formato do plano e "sem base suficiente";
  8. respostas em português, curtas.
- `agent_prompt(agent, reference_date, origin)`: papel, data de referência (com as ferramentas de data e "não use datas depois dela"), **origem do texto do turno** (usada como `source` nas ferramentas que têm esse campo), regras e os fluxos do agente. O grafo passa `state["origin"]`.
- Fluxos (`FLOWS`):
  - **rodada diária** (Vagas): `daily_summary` e `pending_followups` com a data; no máximo cinco ações priorizadas; sem gravação;
  - **registrar fato** (Network: contatos e interações; Vagas: status e etapas): consultar o registro, propor só o que o texto afirma, perguntar se faltar data, resultado ou registro;
  - **avaliar vaga** (Vagas): `search_knowledge` (estratégia e notas), `list_contacts` com `company` e `network_company_overview`; nota, prós, contras, lacunas e quem da rede ajuda; `add_job` só com empresa, título e endereço presentes no texto;
  - **redigir mensagem** (os dois): fatos do servidor, texto curto no tom do canal, para a pessoa revisar e enviar;
  - **preparar entrevista** (Vagas): vaga e etapas do servidor e base de conhecimento; pauta curta com fonte em cada item.
- `DECLINE["refuse"]` reescrita: diz o que fica com a pessoa e o que o agente pode fazer (redigir, revisar, organizar).

**Decisões**

- `log_interaction` não tem `source` na v0.2.0 do servidor (Q4); a instrução manda usar a origem só nas ferramentas que têm o campo, e a origem continua no rastro (`turns.origin`).
- Os testes de fluxo verificam o *harness* (rota seguida, ferramentas do roteiro permitidas e chamadas, argumentos no rastro, proposta presente ou ausente, prompt recebido); a qualidade das respostas depende do modelo real.

**Testes**

- `tests/test_prompts.py` (29 testes): cada regra da decisão 0002, "perguntar quando faltar dado", citação e "sem base suficiente" nas instruções dos dois agentes; data e origem no prompt; fluxos anexados ao agente certo (rodada diária com cinco ações e sem gravação; avaliar vaga com `list_contacts` por empresa); roteador com exemplo de cada rota e os quatro pedidos de recusa; respostas de `decline` sem promessa de envio, publicação, login, candidatura, aceite ou resposta.
- `tests/test_graph_flows.py` (7 testes, servidor real com `data/demo/`, modelo simulado): rodada diária só com leituras (`daily_summary`, `pending_followups` com `reference_date`) e sem proposta; registrar fato (origem `print` no prompt, `list_contacts` e `log_interaction` com proposta); avaliar vaga com a leitura de apoio e proposta de `add_job`; redigir mensagem sem proposta; preparar entrevista com `search_knowledge` e citação; **dado faltante** ("registre que fiz uma entrevista no Banco Aurora"): só `list_jobs`, resposta com pergunta, sem proposta; pedido de envio recusado sem ferramentas.

```text
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict   -> 118 passed (3 min 20 s); ruff limpo; validação estrita sem falhas
.venv\Scripts\python.exe -m ruff format --check src tests          -> 24 files already formatted
```

**Pendências**

- [ ] Verificação manual curta com modelo real (fora do CI) de um caso de cada fluxo e de um pedido com dado faltante: precisa da chave do autor; anotar aqui ao rodar (a evidência formal fica na tarefa 10).
- A suíte passou de 3 minutos porque cada teste de grafo inicia o servidor (cerca de 2,5 s por partida). Se pesar no CI, compartilhar o adaptador por módulo nos testes de leitura.

## Status

```text
concluída nos critérios automáticos; verificação manual com modelo real pendente da chave do autor
```
