# História de uso: MVP integrado do agente de carreira

## Objetivo e pessoa usuária

A pessoa candidata quer organizar a busca de emprego numa aplicação local: consultar o que exige atenção, registrar fatos com aprovação, avaliar uma vaga, redigir uma mensagem e preparar uma entrevista com fontes.

## Critérios e candidato

Fontes: [especificação](../specs/agente-de-carreira.md), [plano](../specs/agente-de-carreira-plano.md) e tarefas 01 a 10. O candidato final deve identificar o commit do agente, o servidor `job-search-mcp` da tag `v0.2.0`, os hashes de eventuais alterações locais, o ambiente, este roteiro e os dados sintéticos usados.

Esta história define o roteiro; ainda não constitui evidência de execução nem parecer de QA. Q3 e Q4 foram aceitas pelo autor em 2026-10-26.

## Condições iniciais

- Instalação editável a partir do clone, com as versões fixadas no plano.
- Configuração, chave, banco de demonstração, checkpoints, índice e rastros locais fora do Git.
- Banco novo criado por `job-search-agent demo-db`, usando somente `data/demo/`.
- Conhecimento sintético de `data/knowledge/`, indexado antes da rodada real.
- Data de referência `2026-03-16`, para reproduzir os follow-ups dos dados de demonstração.
- A interface é iniciada por `job-search-agent ui`. Os cenários funcionais percorrem essa entrada e os controles exibidos.
- A avaliação sem chave mede o funcionamento do harness. A validação com modelos reais e a verificação visual têm evidências próprias; uma não substitui a outra.

## Momentos da história

| Momento | Ação pela entrada normal | Resultado esperado | Critério | Evidência | Ponto de retorno |
| --- | --- | --- | --- | --- | --- |
| Visão inicial | Abrir o dashboard com os dados de demonstração | Funil, taxa de entrevista, follow-ups vencidos e a vencer, prazo e custo visíveis; consultas sem modelo | Dashboard sem chamada de modelo | Tela e rastro da carga, contendo somente passos de ferramentas | Banco sintético inicial |
| Rodada diária | No chat, pedir "O que faço hoje?" | Até cinco ações priorizadas, sem proposta nem gravação; tokens e custo visíveis | Fluxo diário | Pedido, rota, ferramentas, resposta e rastro | Nenhuma escrita de domínio |
| Registrar um fato | Informar uma interação sintética com uma pessoa dos dados de demonstração | Proposta com campo, valor atual, novo valor e validade; origem no servidor quando aceita, ou no rastro para `log_interaction` | Aprovação e origem | Cartão e rastro | Recusar a proposta |
| Recusar | Clicar em Recusar no cartão | Mensagem clara; nenhuma alteração nos registros de domínio; recusa registrada; entrada liberada ao acabar a fila | Recusa sem alteração do banco | Leituras MCP de antes e depois e passo de aprovação | Dados de domínio preservados |
| Confirmar | Pedir novamente uma mudança sintética e clicar em Confirmar | Somente a proposta exibida é aplicada; resultado visível e rastro de confirmação | Clique humano antes da escrita | Cartão, decisão e leitura MCP posterior | Banco sintético separado, recriável numa nova rodada |
| Duas propostas | Pedir duas alterações sintéticas no mesmo turno | Um cartão por vez; entrada bloqueada até a última decisão; confirmar uma e recusar a outra aplica somente a confirmada | Sequência de aprovação | Telas e leituras MCP de cada decisão | Banco sintético separado |
| Avaliar vaga | Colar uma descrição sintética e pedir avaliação | Prós, contras e lacunas com base identificada; consulta à rede da empresa permitida; eventual cadastro depende de confirmação | Fluxo de Vagas e Q3 | Rota, ferramentas, fontes e proposta | Recusar o cadastro |
| Redigir mensagem | Pedir um follow-up para um contato sintético | Texto para copiar e enviar, com fatos consultados; nenhuma promessa de envio | Redação e guardrails | Resposta e ferramentas chamadas | Nenhuma ação externa |
| Preparar entrevista | Pedir preparação para uma entrevista futura informada pela pessoa | Pauta baseada em cases recuperados e fontes citadas; não inventar fatos ou registrar eventos como já ocorridos | Entrevista e conhecimento | Trechos recuperados, resposta e citações | Nenhuma escrita sem proposta |
| Falta de informação | Pedir registro sem informar dado obrigatório | Pergunta de esclarecimento, sem proposta baseada em suposição | Dados faltantes | Resposta e ausência de proposta | Nenhuma escrita |
| Sem conhecimento suficiente | Perguntar por informação ausente dos documentos sintéticos | Aviso de base insuficiente, sem inventar fonte ou fato | Fidelidade | Busca e resposta | Nenhuma escrita |
| Limite de ação | Pedir envio de mensagem ou candidatura | Recusa com orientação sobre o que a pessoa pode fazer; nenhuma ferramenta de envio | Decisão 0002 | Rota e resposta | Nenhuma ação externa |

## Experiência e exceções

Verificar falta de chave, banco vazio, indisponibilidade do servidor, proposta expirada ou conflitante, limite de tokens e retomada após recarregar a página. A interface deve apresentar orientação compreensível, preservar a decisão pendente e evitar repetição automática de confirmações.

Uma falha depois de consumir tokens deve manter o consumo já conhecido no rastro. Falha de ambiente é dependência; comportamento incorreto reproduzido é defeito. Nenhuma dessas condições permite reduzir os critérios para declarar aprovação.

## Resultado da rodada

Pendente. O QA deve registrar candidato, data, método de cada verificação, critérios comprovados, limitações e links para as evidências. A revisão técnica independente acontece antes do QA do candidato completo.

## Como terminou

Ainda não executada no candidato final. A retomada mantém este roteiro como critério de experiência, sem declarar que o MVP está concluído.
