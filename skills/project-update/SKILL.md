---
name: project-update
description: "Compara e atualiza componentes do template numa base já instalada, preservando adaptações e conteúdo do projeto mediante revisão explícita. Não executa atualização automática nem migra aplicação."
---

# Skill: project-update

## Nome

project-update

## Objetivo

Atualizar a base de trabalho com IA sem perder decisões locais ou confundir componentes do template com conteúdo do projeto.

## Categoria

workflow

## Entradas

Projeto de destino, manifesto instalado, versão de origem e versão proposta do template, componentes solicitados e autorização.

## Saídas

Comparação revisável, componentes aprovados atualizados, adaptações preservadas, origem revisada e validação.

## Pré-condições

Leia instruções do destino. Fonte proposta e base instalada devem estar identificadas; se a base antiga não estiver disponível, declare a limitação antes de propor substituições. Caminhos são relativos à raiz.

## Passos

1. Inspecione manifestos, origem registrada, alterações locais, política de branches e caminhos gerenciados e próprios do projeto.
2. Compare base antiga, destino adaptado e versão proposta por arquivo. Se a base antiga faltar, faça comparação de duas versões e não presuma que divergência é obsolescência.
3. Prepare proposta com alterações, conflitos, impacto e recuperação. Atualização é sempre explícita e revisada; apresente governança protegida e formatos externos antes de obter aprovação aplicável.
4. Aplique somente os componentes autorizados na branch definida pela política local. Preserve README próprio, aplicação, specs, tasks, decisões, histórias, evidências, dados, .env e configurações locais.
5. Trate os caminhos gerenciados como inventário, não como autorização de sobrescrita. Quando houver sobreposição com caminho próprio, o conteúdo real do projeto é preservado; READMEs estruturais exigem revisão de suas adaptações.
6. Edite skills apenas na fonte skills/ e sincronize as cópias quando autorizado. Confira diffs e hashes dos arquivos preservados.
7. Atualize a versão e o registro de origem somente para o conjunto realmente aplicado, descrevendo omissões e componentes que permanecem na versão anterior. Execute validações pertinentes e relate lacunas.

## Critérios de sucesso

Atualização revisada e rastreável; decisões locais e conteúdo preservados; versão registrada sem afirmar atualização completa quando parcial; validações observadas.

## Efeitos colaterais

Altera arquivos locais explicitamente aprovados. Não apaga dados, redefine histórico, faz push, migra aplicação ou ativa atualização recorrente.

## Exemplo

Entrada: atualizar papéis e modelos numa base com instruções locais adaptadas. Ação: comparar versões e preservar a política de branches do destino, aplicando o conjunto aprovado. Resultado: papéis atualizados com divergências documentadas e conteúdo real intacto.

## Testes recomendados

Atualização com base conhecida; base indisponível; adaptação local conflitante; atualização parcial; conteúdo próprio e dados preservados; cópias de skills equivalentes.
