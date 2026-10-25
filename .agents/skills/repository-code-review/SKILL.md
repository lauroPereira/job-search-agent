---
name: repository-code-review
description: "Use para revisar código, diffs ou pull requests em busca de riscos de segurança, regressões, complexidade desnecessária e lacunas de testes. Não use para implementar correções sem solicitação explícita."
---

<!-- Papel: procedimento de revisão de código para identificar riscos, simplificar mudanças e avaliar testes. -->

# Skill: repository-code-review

## Nome

repository-code-review

## Objetivo

Revisa código com foco em segurança, simplicidade, mudanças cirúrgicas, qualidade dos testes e aderência às instruções do projeto.

## Categoria

workflow

## Entradas

- Objetivo da mudança.
- Diff, arquivos alterados ou pull request.
- Instruções em AGENTS.md, CLAUDE.md e documentação relevante.

## Saídas

- Achados priorizados, com localização, impacto e sugestão de correção.
- Confirmação das validações realizadas ou lacunas encontradas.

## Pré-condições

- O escopo da mudança está disponível para inspeção.
- A documentação relevante foi lida.

## Passos

1. Entenda o objetivo, os contratos afetados e os riscos antes de avaliar a implementação.
2. Verifique segurança: validação de entradas, autorização, segredos, injeções, exposição de dados e efeitos externos.
3. Verifique simplicidade: abstrações, dependências, duplicações e refatorações sem necessidade.
4. Verifique aderência às regras Karpathy: planejamento, menor solução, mudanças cirúrgicas e validação guiada por metas.
5. Verifique testes de sucesso, erro, limite e regressão proporcional ao impacto.
6. Classifique os achados por prioridade e informe a evidência.
7. Não edite código durante a revisão, salvo solicitação explícita.

## Critérios de sucesso

- Riscos relevantes são identificados com contexto suficiente para correção.
- A revisão distingue defeitos de sugestões opcionais.
- A conclusão informa se testes e validações são suficientes.

## Efeitos colaterais

Nenhum. A skill produz análise; qualquer alteração de código exige solicitação explícita e segue a política de confirmação do repositório.

## Exemplo

Achado: uma rota pública aceita um identificador sem validação e o usa em uma consulta. Impacto: entrada malformada pode gerar erro ou consulta indevida. Sugestão: validar formato e adicionar testes para identificador válido e inválido.

## Testes recomendados

- Revisar uma mudança simples com testes de sucesso e erro.
- Revisar uma mudança que introduz uma dependência desnecessária.
- Revisar uma mudança de contrato público sem plano de compatibilidade e confirmar que ela é apontada como bloqueadora.
