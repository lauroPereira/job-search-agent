---
name: qa
description: "Valida a entrega pela história de uso no candidato fixado quando o Supervisor despacha o papel QA. Não julga arquitetura de código, altera produto ou decide publicação."
---

# Skill: qa

## Nome

qa

## Objetivo

Exercer o papel QA do fluxo com responsabilidades e evidências explícitas.

## Categoria

workflow

## Entradas

Tarefa ou entrega, critérios, referências, candidato, ambiente quando pertinente e autorização vigente.

## Saídas

Parecer funcional, evidências da história, defeitos, limitações e como terminou.

## Pré-condições

Localize a raiz do projeto e leia AGENTS.md. Caminhos desta skill são relativos à raiz, mesmo quando a skill foi descoberta numa cópia gerada.
Candidato e critérios identificados; não presuma UI web ou ambiente hospedado.

## Passos

1. Leia `docs/wiki/agents/qa.md` e o protocolo em `docs/wiki/agents/README.md`.
2. Confirme tarefa, critérios, versões e limites antes de agir.
3. Execute verificações pertinentes e percorra a história pela entrada normal, inspecionando a evidência antes de seguir.
4. Registre esperado e observado; defeito vira tarefa, ambiente indisponível vira bloqueio e dúvida de escopo vai ao Supervisor.
5. Devolva a passagem com candidato, evidência e próximo responsável, usando `docs/templates/passagem-de-papel.md`. Não despache outros agentes nem realize ações externas sem autorização.

## Critérios de sucesso

Critérios avaliados com evidência ligada à versão; lacunas e bloqueios explícitos; limites do papel respeitados.
Resultado apto, reprovado ou bloqueado distingue produto, experiência e dependência.

## Efeitos colaterais

Execução em ambiente de teste e criação de relatório ou tarefa autorizada; nenhuma integração ou publicação.

## Exemplo

Entrada: entrega de exportação de relatório. Ação: percorrer obtenção dos dados, exportação e leitura do arquivo como usuário. Resultado: evidência do fluxo completo e tarefa para defeito reproduzido.

## Testes recomendados

Caminho principal com critérios comprovados; dependência indisponível; versão alterada; operação fora da autorização; preservação dos limites do papel.
