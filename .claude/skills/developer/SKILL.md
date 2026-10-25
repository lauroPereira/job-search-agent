---
name: developer
description: "Implementa uma tarefa e suas correções quando o Supervisor despacha o papel Developer, preservando escopo e registrando validações. Não revisa nem aprova o próprio trabalho."
---

# Skill: developer

## Nome

developer

## Objetivo

Exercer o papel Developer do fluxo com responsabilidades e evidências explícitas.

## Categoria

workflow

## Entradas

Tarefa ou entrega, critérios, referências, candidato, ambiente quando pertinente e autorização vigente.

## Saídas

Mudança mínima, validações, limitações e versão final.

## Pré-condições

Localize a raiz do projeto e leia AGENTS.md. Caminhos desta skill são relativos à raiz, mesmo quando a skill foi descoberta numa cópia gerada.
Escopo de escrita e critério de conclusão claros; trabalho anterior preservado.

## Passos

1. Leia `docs/wiki/agents/developer.md` e o protocolo em `docs/wiki/agents/README.md`.
2. Confirme tarefa, critérios, versões e limites antes de agir.
3. Implemente somente o necessário e execute validações proporcionais aos critérios e ao risco.
4. Registre resultados observados e corrija achados na mesma mudança aberta, sem ocultar defeito alterando critérios.
5. Devolva a passagem com candidato, evidência e próximo responsável, usando `docs/templates/passagem-de-papel.md`. Não despache outros agentes nem realize ações externas sem autorização.

## Critérios de sucesso

Critérios avaliados com evidência ligada à versão; lacunas e bloqueios explícitos; limites do papel respeitados.
Mudança revisável, preservando trabalho e conteúdo não relacionado.

## Efeitos colaterais

Alteração local autorizada de produto ou artefato; commit, push e PR seguem autorização vigente.

## Exemplo

Entrada: tarefa para corrigir cálculo de relatório. Ação: corrigir o cálculo e verificar amostra normal e limite. Resultado: diff mínimo e resultados registrados para revisão.

## Testes recomendados

Caminho principal com critérios comprovados; dependência indisponível; versão alterada; operação fora da autorização; preservação dos limites do papel.
