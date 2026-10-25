# Perfil develop: dev, hml e prd

Texto pronto para um projeto que adota o perfil `develop` de `workflow.json`. Substitua a seção "Fluxo de branches" do `AGENTS.md` e do `CLAUDE.md` do projeto pelo bloco abaixo e ajuste `default_profile` para `develop`. A adoção exige aprovação do responsável humano.

```markdown
## Fluxo de branches

Este projeto usa três estágios:

| Estágio | Onde vive | Como se chega lá |
|---|---|---|
| **dev** (desenvolvimento) | branch `develop` | pull request de uma branch de trabalho para `develop`, com revisão |
| **hml** (homologação) | branch `main` | pull request de `develop` para `main`, quando a entrega está completa e o QA aprovou |
| **prd** (produção) | tag `v*.*.*` em `main` | tag de versão semântica criada sobre um commit de `main`, por decisão do responsável humano |

Antes de realizar qualquer tipo de alteração em diretórios ou arquivos, atualize e parta de `develop` — nunca da branch de trabalho atual nem de `main`.

1. Mude para `develop`.
2. Atualize `develop` (`git pull`).
3. Crie a branch de trabalho a partir da `develop` atualizada, no formato `<tipo>/<tarefa>-<assunto>` (por exemplo, `feat/02-banco-e-dados`).

Só então aplique alterações e commits e abra o pull request para `develop`.

Regras:

- Nenhum commit direto em `develop` nem em `main`: tudo entra por pull request.
- `main` só recebe pull requests vindos de `develop`. Correção urgente em `main` exige aprovação explícita do responsável humano e deve voltar para `develop` em seguida.
- Antes de promover para `main`, todos os pull requests da entrega devem estar integrados em `develop`.
- A promoção para `main` (hml) e a criação de tag (prd) dependem de autorização explícita do responsável humano; agentes preparam o pull request ou a proposta de versão e param.
- Tags seguem versionamento semântico (`vMAIOR.MENOR.CORREÇÃO`) e só são criadas sobre commits de `main`.
```

## Notas

- Crie `develop` a partir de `main` logo depois do primeiro commit do projeto.
- O workflow `validate.yml` do template já roda em `develop`, em `main` e nas tags `v*.*.*`.
- Origem: perfil adotado no projeto job-search-mcp (2026-10-10), que chegou à `v0.1.0` com esse fluxo.
