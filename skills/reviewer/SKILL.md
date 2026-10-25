---
name: reviewer
description: "Emite revisão técnica independente quando o Supervisor despacha o papel Reviewer, re-derivando critérios e evidência. Não implementa correções nem substitui QA."
---

# Skill: reviewer

## Nome

reviewer

## Objetivo

Exercer o papel Reviewer do fluxo com responsabilidades e evidências explícitas.

## Categoria

workflow

## Entradas

Tarefa ou entrega, critérios, referências, candidato, ambiente quando pertinente e autorização vigente.

## Saídas

Parecer técnico, independência, achados reproduzíveis e evidência própria.

## Pré-condições

Localize a raiz do projeto e leia AGENTS.md. Caminhos desta skill são relativos à raiz, mesmo quando a skill foi descoberta numa cópia gerada.
Confira que o contexto é separado do implementador; se não for, registre não-independente.

## Passos

1. Leia `docs/wiki/agents/reviewer.md` e o protocolo em `docs/wiki/agents/README.md`.
2. Confirme tarefa, critérios, versões e limites antes de agir.
3. Inspecione a mudança e execute verificações próprias; use skills/repository-code-review/SKILL.md quando houver código.
4. Registre condição, impacto, localização e reprodução de cada achado; correções voltam ao Developer.
5. Devolva a passagem com candidato, evidência e próximo responsável, usando `docs/templates/passagem-de-papel.md`. Não despache outros agentes nem realize ações externas sem autorização.

## Critérios de sucesso

Critérios avaliados com evidência ligada à versão; lacunas e bloqueios explícitos; limites do papel respeitados.
Independência declarada corretamente, sem autoaprovação.

## Efeitos colaterais

Inspeção e execução de verificações; review na plataforma somente se autorizada.

## Exemplo

Entrada: CLI promete aceitar arquivo vazio. Ação: testar essa entrada no candidato, inspecionar o diff e registrar o comportamento. Resultado: parecer com evidência própria e versão.

## Testes recomendados

Caminho principal com critérios comprovados; dependência indisponível; versão alterada; operação fora da autorização; preservação dos limites do papel.
