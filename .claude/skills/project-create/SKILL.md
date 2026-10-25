---
name: project-create
description: "Prepara um projeto novo como snapshot independente do ai-dev-template, para qualquer foco ou tecnologia, inclusive ainda indefinida. Não prepara destino ocupado nem implementa produto por inferência."
---

# Skill: project-create

## Nome

project-create

## Objetivo

Preparar a base de um projeto novo: identidade, contexto, instruções, papéis, skills e validações, sem dependência do template nem tecnologia presumida.

## Categoria

workflow

## Entradas

- Nome do projeto em kebab-case, objetivo ou descrição e diretório de destino: obrigatórios antes da criação.
- Tecnologia: definida, **a definir** ou **não se aplica**. Não bloqueie a base por falta de stack; não invente uma.
- Restrições, primeiro resultado verificável e autorização vigente.
- Git e remoto: opcionais; sem pedido, não inicialize repositório nem configure remoto.
- Branch inicial: main quando Git for solicitado sem outra escolha.
- Docker e SDD: opcionais; ausentes significam não ativar containers nem exigir o fluxo SDD completo.
- Fonte e versão do template: identificar pela raiz e pelo manifesto, sem codificar caminho da máquina.

## Saídas

Projeto independente com README próprio, AGENTS.md e CLAUDE.md adaptados, skills canônicas e cópias geradas, papéis e modelos reutilizáveis, manifesto com template_name e template_version e origem verificável. Primeira tarefa preparada quando fizer parte do pedido.

## Pré-condições

Leia as instruções aplicáveis à fonte e ao destino. O usuário autorizou a criação e o destino. O diretório não existe ou está vazio; se houver conteúdo, encaminhe à preparação de projeto existente e peça aprovação específica antes de escrever.

Os caminhos mencionados nesta skill são relativos à raiz do template ou projeto, não à cópia da skill. Destino fora do workspace exige a autorização operacional correspondente.

## Passos

1. **Entender a intenção.** Reutilize respostas dadas ao Supervisor. Pergunte só objetivo, nome, destino ou decisão material ausentes. Stack pode permanecer a definir e projetos de pesquisa, dados ou documentos não precisam de software.
2. **Verificar o destino.** Confirme caminho absoluto, limites do workspace, conteúdo e possíveis links para outro local. Não grave em diretório ocupado nem sobrescreva README, .env ou arquivos existentes.
3. **Preparar o conjunto concreto.** Apresente arquivos, adaptações, omissões, validação e recuperação. Preserve a política aprovada do projeto. A fonte deste template permanece inalterada ao criar o destino.
4. **Selecionar o snapshot.** Use os componentes reutilizáveis do manifesto: instruções, skills/, docs/templates/, docs/wiki/agents/, READMEs estruturais e scripts pertinentes. Inclua evals/ e seus cenários reutilizáveis para manter as referências e a validação estrutural coerentes. Nunca copie .git, configuração global ou local, .env, dados, segredos, docs/raw/, aplicação, specs, tarefas, decisões, histórias ou evidências reais. Não copie o README humano do template como README do projeto.
5. **Adaptar a base.** Escreva README com nome, objetivo, tecnologia decidida ou pendente, forma de trabalho e como validar. Adapte instruções e perfil declarativo às decisões aprovadas, sem importar permissões ou autorizações de outro projeto. Acrescente ao AGENTS.md a seção "Sobre este projeto" com nome, objetivo, stack, convenção de idioma, fluxo e, em repositório público, a regra de privacidade de dados. Se o projeto adotar o perfil develop, aplique o texto de docs/wiki/agents/perfil-develop.md. Não crie src, frontend, backend, Docker ou ambiente de nuvem por suposição.
6. **Tratar SDD proporcionalmente.** Modelos podem permanecer disponíveis. Se SDD não foi solicitado, não crie docs/specs/, docs/tasks/ nem docs/architecture/ como rotina de criação. Remova do manifesto do destino as entradas de estrutura omitidas e adapte orientações que exigiriam esses diretórios. Tarefas e decisões podem ser criadas depois quando fizerem sentido. Histórias e evidências são suporte opcional à entrega, não exigência de processo completo.
7. **Aplicar a autorização.** O pedido de criação já pode autorizar os arquivos novos e destino apresentados; não peça novamente a mesma autorização. Alterações em governança protegida, destino ocupado, fora do workspace e efeitos externos ainda seguem as instruções aplicáveis. Se exigirem decisão, o conjunto deve estar pronto para revisão antes da pergunta.
8. **Registrar a origem.** Grave template_name e template_version em .agent-template.json. Em docs/wiki/origem-template.md, registre versão, commit-base quando houver, data, hashes dos arquivos-fonte copiados, omissões e adaptações. Se a fonte tiver mudanças locais, declare snapshot modificado: commit sozinho não identifica essa cópia. Não registre segredos nem caminho pessoal absoluto.
9. **Gerar descoberta.** Copie skills canônicas e gere .agents/skills/ e .claude/skills/ com tools/scripts/sync-skills.ps1 no destino, quando autorizado. Nunca use cópias geradas divergentes como fonte. Se a plataforma não executar o script, registre a limitação e não afirme descoberta validada.
10. **Validar e encaminhar.** Confira caminhos, manifesto, origem, neutralidade e cópias. Execute validação estrutural e de fluxo, quando disponíveis; validação Python só se pertinente. Confirme preservação do que existia. Se a implementação também estiver no pedido, o Supervisor prepara e despacha a primeira tarefa ao Developer; caso contrário, entregue a base e o próximo passo.

## Critérios de sucesso

- Base utilizável sem foco, nicho, provedor, stack ou nuvem impostos.
- Nome, objetivo e destino são explícitos; tecnologia indefinida é registrada como decisão pendente.
- Origem e versão são verificáveis; o projeto não usa o template como submodule, subtree ou dependência.
- Nenhum arquivo preexistente é sobrescrito e nenhuma autorização alheia é herdada.
- SDD e componentes omitidos são coerentes com instruções e manifesto.
- Skills canônicas e cópias equivalentes, ou limitação de sincronização declarada.
- Base pronta é distinguida de produto implementado, Git inicializado e conteúdo publicado.

## Efeitos colaterais

Cria arquivos novos no destino autorizado. Não apaga arquivos, inicializa Git, altera configuração global, cria remoto, faz commit, push, publicação ou contratação automaticamente.

## Exemplo

Entrada: "Supervisor, crie relatorio-de-pesquisa em <workspace>/relatorio-de-pesquisa para organizar uma pesquisa; ferramentas a definir, sem Git e sem SDD". Ação: verificar destino vazio, apresentar conjunto, preparar contexto e papéis, registrar origem e validar descoberta. Resultado: base independente para pesquisa, sem API, frontend, nuvem ou linguagem escolhida por inferência.

## Testes recomendados

Projeto sem stack; projeto que não é software; destino ocupado com README e .env; projeto sem Git; SDD omitido com manifesto coerente; fonte modificada com hashes; conteúdo real excluído; configuração global preservada; primeira tarefa apenas quando autorizada.
