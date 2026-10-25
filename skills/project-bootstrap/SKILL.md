---
name: project-bootstrap
description: "Prepara a base de trabalho com IA num projeto existente, adaptando instruções, skills e documentação sem sobrescrever trabalho ou impor tecnologia. Não cria projeto novo nem atualiza automaticamente uma base já instalada."
---

# Skill: project-bootstrap

## Nome

project-bootstrap

## Objetivo

Introduzir a base reutilizável num projeto existente, respeitando sua estrutura, instruções e decisões.

## Categoria

workflow

## Entradas

Projeto de destino, fonte e versão do template, objetivo da preparação, restrições e autorização.

## Saídas

Base adaptada, inventário de arquivos preservados, origem, diferenças aprovadas e validações observadas.

## Pré-condições

Destino acessível; instruções locais lidas; fonte identificada. Caminhos desta skill são relativos à raiz do projeto. Destino não vazio não autoriza substituição por inferência.

## Passos

1. Leia AGENTS.md do destino e identifique estrutura, arquivos existentes, repositórios reais, validações e base anterior. Raiz sem Git pode reunir vários repositórios; não inicialize Git por suposição.
2. Leia o manifesto da fonte e inventarie apenas componentes reutilizáveis. Não importe conteúdo real, histórias, evidências, dados, segredos ou autorizações de outro projeto.
3. Prepare comparação por arquivo: ausente, equivalente ou divergente. Apresente conjunto concreto antes de pedir aprovação para governança protegida, conflitos ou escrita em destino ocupado.
4. Adapte README, instruções e comandos à realidade do projeto. Não imponha stack, modelo, nuvem, banco, branch ou SDD. Use os papéis em docs/wiki/agents/ quando esse fluxo for desejado.
5. Aplique somente os arquivos autorizados, preservando aplicação, documentos brutos, .env, histórico e configurações locais. Não opere automaticamente nos repositórios filhos.
6. Registre origem, versão, commit quando houver, hashes do snapshot, omissões e adaptações em docs/wiki/origem-template.md. Registre template_name e template_version no manifesto sem descartar campos próprios do projeto.
7. Sincronize skills a partir de skills/ com tools/scripts/sync-skills.ps1 quando a operação estiver autorizada. Confira equivalência das cópias e execute validações pertinentes; não confunda base pronta com aplicação validada.

## Critérios de sucesso

Base utilizável no contexto real; arquivos anteriores preservados; mudanças rastreáveis; origem verificável; nenhuma infraestrutura ou publicação presumida.

## Efeitos colaterais

Cria ou adapta arquivos locais aprovados num projeto existente. Não altera configuração global, credenciais, remotos, dados ou repositórios filhos por padrão.

## Exemplo

Entrada: diretório de pesquisa com documentos existentes e sem Git. Ação: comparar a base, apresentar arquivos novos e adaptações, obter aprovação necessária e preservar documentos. Resultado: contexto e skills disponíveis sem criar aplicação ou repositório por suposição.

## Testes recomendados

Projeto sem Git; raiz com repositórios filhos; AGENTS.md divergente; README e .env preservados; material real excluído; origem registrada e sincronização verificada.
