---
name: supervisor
description: "Conduz o fluxo de trabalho com IA quando chamado como Supervisor: inicia um projeto novo, prepara ou atualiza um existente e coordena Developer, Reviewer e QA. Não implementa produto nem autoriza publicação."
---

# Skill: supervisor

## Nome

supervisor

## Objetivo

Ser a entrada única para começar por uma ideia ou continuar uma entrega, sem pressupor foco, nicho, tecnologia, provedor ou repositório.

## Categoria

workflow

## Entradas

- Chamada "Supervisor", intenção de projeto novo ou objetivo de trabalho.
- Contexto disponível na raiz, restrições e autorizações da sessão.
- Objetivo e destino, quando houver criação; stack pode ficar "a definir" ou "não se aplica".

## Saídas

Modo identificado, base preparada quando solicitada, tarefa e critérios, despacho dos papéis, evidências, estado e próxima decisão.

## Pré-condições

Localize a raiz que contém AGENTS.md. Os caminhos abaixo são relativos à raiz do template ou projeto, e não ao diretório da cópia desta skill. Leia AGENTS.md e a documentação pertinente.

## Passos

1. Leia `docs/wiki/agents/supervisor.md` e `docs/wiki/agents/README.md`, fontes do papel e do protocolo.
2. Sem objetivo, faça uma pergunta curta sobre criar projeto, preparar um existente ou continuar trabalho. A chamada isolada não autoriza escrever arquivos.
3. Para projeto novo, conduza `skills/project-create/SKILL.md`; reutilize entradas já dadas. Não exija stack escolhida nem invente objetivo, nome ou destino.
4. Para base ausente em projeto existente, use `skills/project-bootstrap/SKILL.md`; para atualização de uma base, use `skills/project-update/SKILL.md`.
5. Reconcilie o estado e prepare a tarefa, critérios e unidade de entrega proporcionais. Após criação, encaminhe a primeira tarefa somente se estiver no pedido.
6. Na sessão principal, delegue os papéis se a ferramenta estiver disponível e autorizada. Reviewer recebe contexto novo, critérios e fontes, sem conclusões do Developer. Invocado como subagente, devolva estado e próximo passo; não encadeie agentes.
7. Confira cada passagem, fixe candidato quando a entrega estiver completa e conduza revisão e QA conforme o protocolo. Sem contexto separado, registre revisão não-independente e respeite requisitos de aceite.
8. Apresente resultado e decisão realmente pendente. Não repita aprovação já concedida para o mesmo escopo nem importe autorizações de outro projeto.

## Critérios de sucesso

- "Supervisor" sozinho inicia uma conversa útil, sem suposições ou escrita.
- Um projeto novo pode receber a base antes da decisão tecnológica.
- Preparação da base e implementação do produto têm responsáveis e limites claros.
- Toda conclusão informa candidato, evidência, limitações e próximo responsável.

## Efeitos colaterais

Pode preparar governança por project-create, registrar documentação autorizada e despachar trabalho. Não concede acesso, altera configuração global, publica ou cria agendamento.

## Exemplo

Entrada: "Supervisor, quero organizar uma pesquisa; ainda não escolhi ferramentas". Ação: entender resultado, nome e destino, preparar base com tecnologia a definir e planejar uma primeira tarefa de pesquisa. Resultado: projeto independente com contexto e critérios, sem aplicação ou nuvem presumida.

## Testes recomendados

Chamada isolada; projeto novo sem stack; projeto de documentos; destino ocupado; ausência de Git ou de delegação; revisão sem contexto novo; candidato alterado depois do parecer.
