<!-- Papel: instruções específicas para Claude Code trabalhar de forma segura e consistente neste repositório. -->

# CLAUDE.md

## 4 regras Karpathy

1. **Pensar antes de codar.** Entenda o objetivo, o contexto, os riscos e o menor plano viável antes de alterar qualquer arquivo.
2. **Simplicidade.** Escolha a solução mais simples, clara e suficiente; evite abstrações, dependências e escopo prematuros.
3. **Mudanças cirúrgicas.** Altere somente o necessário para cumprir a meta, preservando comportamentos e arquivos não relacionados.
4. **Execução guiada por metas.** Defina critérios verificáveis, execute o plano, valide o resultado e relate evidências objetivas.

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

## Uso deste repositório no Claude Code

- As skills ficam em skills/, a fonte canônica. `.claude/skills/` e `.agents/skills/` são cópias geradas por tools/scripts/sync-skills.ps1: não edite esses diretórios diretamente. Cada skill deve ter seu próprio diretório e arquivo SKILL.md.
- A documentação fica em docs/: raw/ contém materiais brutos, wiki/ contém conteúdo revisado e templates/ contém modelos reutilizáveis.
- O suporte a SDD é opcional: specs em docs/specs/, tarefas em docs/tasks/ e decisões arquiteturais em docs/architecture/decisions/. A regra de quando aplicá-lo está em docs/specs/README.md e em AGENTS.md.
- Para preparar um novo projeto a partir deste template, use a skill project-create; o projeto recebe um snapshot independente, sem submodule.
- Ao ser chamado como Supervisor, use skills/supervisor/SKILL.md e docs/wiki/agents/supervisor.md: identifique criação, preparação, atualização ou continuidade, sem exigir tecnologia já escolhida.
- O protocolo em docs/wiki/agents/README.md organiza Supervisor, Developer, Reviewer e QA. A sessão principal coordena; delegação depende de ferramenta e autorização disponíveis, e revisão independente exige contexto novo.
- Antes de commit, merge ou tag, confira a identidade do Git contra a definida para o projeto; se divergir, pare e pergunte. Integre por merge local quando a conta da interface web usar outra identidade (detalhes em AGENTS.md, "Identidade e integração").
- As skills dos papéis são portáteis; este template não instala configurações nativas de subagentes. Descrições de papel não concedem permissões nem substituem a política de branches.
- Leia a documentação pertinente em docs/ antes de modificar código.
- Não edite, mova, renomeie ou apague arquivos em docs/raw/.
- Use os scripts determinísticos de tools/scripts/ para validações repetíveis. Para projetos com Python, execute python tools/scripts/lint_and_tests.py quando aplicável.
- Proponha alterações em AGENTS.md e CLAUDE.md somente por pull request ou comentário. Nunca edite esses arquivos autonomamente sem aprovação explícita do usuário.
- Respeite a política de confirmação de AGENTS.md para operações destrutivas, contratos públicos, dados, permissões e efeitos externos.

## Forma de trabalho esperada

1. Leia instruções e documentação relevantes.
2. Explique o plano mínimo e os riscos importantes.
3. Faça mudanças simples e cirúrgicas.
4. Execute validações proporcionais ao impacto.
5. Relate arquivos alterados, resultados e pendências.
