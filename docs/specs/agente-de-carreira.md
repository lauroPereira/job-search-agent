# Especificação: agente de carreira (v0.1)

Status: **rascunho**, aguardando as questões em aberto. Cliente do servidor [job-search-mcp](https://github.com/lauroPereira/job-search-mcp), a partir da versão `v0.2.0` ("fonte única"). O modelo de domínios e a matriz de cobertura que orientam esta especificação estão no [modelo de domínios](https://github.com/lauroPereira/job-search-mcp/blob/develop/docs/specs/modelo-de-dominios.md) do servidor.

## Problema

Gerir uma recolocação com agentes de IA, todos os dias, mostrou cinco problemas que o servidor sozinho não resolve:

- **Não há visão do todo sem perguntar ao agente.** O funil e os follow-ups saem de uma conversa, gastando tokens com o que é uma consulta fixa.
- **Os fluxos se repetem e são refeitos a cada sessão:** a rodada diária, o registro de um fato a partir de um print ou áudio, a avaliação de uma vaga, a redação de uma mensagem, a preparação de uma entrevista.
- **O conhecimento acumulado não é consultável:** descrições de vagas, notas de empresas e entrevistas, cases e a estratégia de carreira ficam em documentos soltos; o agente relê ou esquece.
- **O agente afirma e grava por suposição** e mistura fatos de fontes diferentes.
- **Não há medida de qualidade nem de custo** das respostas.

## Usuário afetado

A pessoa candidata, no uso diário; e quem avalia o projeto como portfólio, que precisa ver o funcionamento, as métricas e as decisões.

## Resultado desejado

Uma aplicação local com um dashboard e um chat. O chat aceita pedidos em linguagem natural; um supervisor encaminha para o agente do domínio; o agente consulta o servidor e a base de conhecimento, responde citando a fonte e, quando há alteração, mostra a proposta do servidor e só confirma com a aprovação da pessoa. Cada resposta mostra tokens e custo; a qualidade é medida por um conjunto de avaliação versionado.

## Escopo

- Supervisor e agentes dos domínios disponíveis no servidor `v0.2.0`: **Network** e **Vagas**; os agentes de Perfil e Desenvolvimento entram quando o servidor tiver esses domínios.
- Fluxos (skills do grafo): rodada diária, registrar fato, avaliar vaga, redigir mensagem, preparar entrevista.
- Base de conhecimento local com busca semântica, como ferramenta compartilhada pelos agentes.
- Interface Streamlit: um dashboard (funil, follow-ups, custo do agente) e o chat com a proposta de alteração e os botões de confirmar e recusar.
- Conjunto de avaliação (15 a 20 casos) e execução automatizada.
- Rastro de cada conversa (passos, ferramentas, tokens, custo) gravado localmente.
- Dados e documentos sintéticos de demonstração.

## Fora do escopo

- **Próxima entrega:** relatório semanal, Langfuse e geração de currículo e carta.
- Enviar mensagens, e-mails, candidaturas ou posts; fazer login; preencher formulários; responder testes ([decisão 0002](../architecture/decisions/0002-acoes-externas-ficam-com-a-pessoa.md)).
- Ler Gmail, WhatsApp ou LinkedIn (os fatos entram colados no chat, como texto, print ou transcrição).
- Agente editorial de posts.
- Multiusuário, autenticação e hospedagem em nuvem.
- Carga dos dados reais (feita depois da v1, só na máquina do usuário).

## Requisitos funcionais

### Orquestração
- O supervisor deve encaminhar cada pedido a um agente de domínio ou responder que o pedido está fora do escopo.
- Cada agente deve receber só as ferramentas MCP do próprio domínio e a busca no conhecimento.
- O agente não deve inventar status, datas ou valores que a pessoa não informou; quando faltar dado, pergunta.

### Gravação com aprovação
- Toda alteração deve passar pela proposta do servidor; a interface deve mostrar o que muda (campo, valor atual, valor proposto) e só confirmar com o clique da pessoa.
- A recusa não deve alterar nada e deve ficar registrada no rastro.
- A origem da alteração (conversa, print, áudio, e-mail) deve ser enviada ao servidor.

### Conhecimento
- O sistema deve indexar documentos locais (descrições de vagas, notas de empresas e entrevistas, cases, estratégia) e responder com trechos recuperados, citando a fonte.
- Sem base suficiente, a resposta deve dizer isso em vez de completar com suposição.

### Interface e relatórios
- O dashboard deve mostrar o funil por status, a taxa de entrevista, os follow-ups vencidos e a vencer, os dias até o prazo-âncora e o custo do agente no período, por consulta ao servidor e ao rastro, sem chamar modelo.
- Cada resposta do chat deve mostrar tokens e custo estimado.

### Avaliação e observabilidade
- O projeto deve ter casos de avaliação versionados: pedido, agente esperado, ferramentas e argumentos esperados e critério da resposta.
- Casos do conhecimento devem indicar o trecho que deveria ser recuperado, para medir recuperação e fidelidade à fonte.
- A avaliação deve rodar no CI sem rede e sem custo (modelo simulado) e, sob demanda, com o modelo real, registrando o resultado.

## Requisitos não funcionais

- **Privacidade:** repositório público, só dados sintéticos; dados reais, base vetorial, rastros e chave de API fora do Git; logs mascaram dados pessoais.
- **Custo:** limite configurável de tokens por turno e por dia; modelo menor para roteamento, maior só onde a qualidade exigir.
- **Provedor:** API da OpenAI, isolada atrás de uma interface do projeto ([decisão 0001](../architecture/decisions/0001-streamlit-langgraph-openai.md)).
- **Execução local** com um comando; testes e avaliação simulada no CI sem chave de API.

## Casos de uso

1. **Rodada diária** — a pessoa abre a aplicação: o dashboard mostra o funil e os vencidos; no chat, "o que faço hoje?" devolve no máximo cinco ações priorizadas, sem gravar nada.
2. **Registrar um fato** — a pessoa cola a resposta de um contato: o agente de Network propõe a interação, o novo status e o próximo passo; a pessoa confirma ou recusa.
3. **Avaliar uma vaga** — a pessoa cola uma descrição: o agente de Vagas dá nota com prós e contras, aponta lacunas e quem da rede está na empresa, e propõe o cadastro.
4. **Redigir mensagem** — "escreva um follow-up para a recrutadora": o agente redige no tom e no canal certos, com os fatos do servidor; a pessoa copia e envia.
5. **Preparar entrevista** — "prepare a entrevista técnica de amanhã": o agente monta a pauta com os cases da base de conhecimento, citando a fonte.

## Critérios de aceitação

- [ ] Os cinco casos de uso funcionam com os dados sintéticos, com evidência em `docs/evidence/`.
- [ ] Teste: recusar a proposta não altera o banco do servidor.
- [ ] Teste: cada agente só vê as ferramentas do seu domínio.
- [ ] A avaliação roda no CI sem chave de API e tem um resultado de referência com o modelo real registrado.
- [ ] A avaliação do conhecimento reporta acerto na recuperação e fidelidade à fonte.
- [ ] Toda resposta mostra tokens e custo; o rastro de uma conversa pode ser aberto localmente.
- [ ] O dashboard não chama modelo (verificável no rastro).
- [ ] Busca nos arquivos versionados não encontra dado real.

## Riscos

- **Escopo para um case curto:** mitigado pelo corte (dois domínios, cinco fluxos, um dashboard) e pela próxima entrega separada.
- **Dados pessoais enviados ao provedor** no uso real. Mitigação: enviar só o necessário, mascarar dados pessoais e decidir os embeddings (Q1).
- **Custo do modelo.** Mitigação: limites por turno e por dia, dashboard sem modelo, custo visível.
- **Avaliação frágil:** mitigação: avaliar principalmente roteamento, ferramentas e argumentos (determinísticos).
- **Dependência da `v0.2.0` do servidor:** o agente é construído contra a especificação e testado com servidor simulado até a versão sair.
- **Mudança frequente de LangChain, LangGraph e Streamlit:** versões fixadas e conferidas antes de cada tarefa.

## Questões em aberto

- **Q1. Embeddings:** pela API da OpenAI (simples, envia o texto ao provedor) ou modelo local (dados não saem da máquina, mais dependências). Responsável: autor.
- **Q2. Modelos:** quais modelos da OpenAI para roteamento e para redação, conferidos no catálogo e nos preços do momento do plano. Responsável: plano técnico.
