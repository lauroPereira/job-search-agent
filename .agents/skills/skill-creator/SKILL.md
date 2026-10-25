---
name: skill-creator
description: "Use para criar ou revisar skills reutilizáveis para Codex e Claude Code, incluindo frontmatter, instruções, exemplos e testes. Não use para tarefas que não envolvam criação ou manutenção de uma skill."
---

<!-- Papel: orientar agentes na criação e revisão de skills completas, testáveis e alinhadas ao template. -->

# Skill: skill-creator

## Nome

skill-creator

## Objetivo

Cria e revisa skills reutilizáveis, seguras, testáveis e compatíveis com Codex e Claude Code.

## Categoria

workflow

## Entradas

- Pedido para criar ou revisar uma skill.
- Contexto, documentação e regras aplicáveis.

## Saídas

- Uma skill completa em skills/nome-em-kebab-case/SKILL.md.
- Exemplo e testes recomendados proporcionais ao risco.

## Pré-condições

- AGENTS.md e a documentação relevante foram lidos.
- O objetivo da skill e a categoria foram definidos.

## Passos

1. Leia AGENTS.md e a documentação relevante em docs/.
2. Defina um nome em kebab-case e use o mesmo valor no diretório e no frontmatter.
3. Comece SKILL.md com frontmatter YAML contendo somente name e description.
4. Escreva na description o que a skill faz, quando deve ser usada e seus limites de ativação.
5. Use a estrutura de docs/templates/modelo-skill.md para o corpo da skill.
6. Escolha uma única Categoria entre conhecimento, capacidade e workflow.
7. Descreva passos mínimos, determinísticos e verificáveis.
8. Declare efeitos colaterais e a confirmação necessária antes de qualquer operação destrutiva.
9. Acrescente um exemplo realista e testes recomendados.
10. Revise se a skill pode ser seguida sem conhecimento implícito essencial.

### Frontmatter obrigatório

```yaml
---
name: nome-da-skill
description: Descreva o que a skill faz, quando deve ser usada e quando não deve ser usada.
---
```

### Definição dos campos obrigatórios

Toda skill deve conter estes campos, nesta ordem:

1. **Nome:** identificador curto e único.
2. **Objetivo:** problema resolvido e resultado desejado.
3. **Categoria:** conhecimento, capacidade ou workflow.
4. **Entradas:** informações, arquivos, ferramentas ou decisões necessárias.
5. **Saídas:** resultado esperado e artefatos produzidos.
6. **Pré-condições:** condições e permissões exigidas antes da execução.
7. **Passos:** sequência mínima, ordenada e verificável.
8. **Critérios de sucesso:** evidências observáveis de conclusão.
9. **Efeitos colaterais:** impactos, riscos, operações externas e confirmações necessárias; escreva Nenhum se não houver.
10. **Exemplo:** entrada, ação e resultado esperado em um cenário realista.
11. **Testes recomendados:** caminho principal, erro ou limite aplicável e verificação de efeitos colaterais.

## Critérios de sucesso

- A skill está em skills/nome-em-kebab-case/SKILL.md.
- SKILL.md começa com frontmatter contendo somente name e description.
- O name corresponde exatamente ao nome do diretório.
- A description informa função, gatilhos e limites da skill.
- Todos os campos obrigatórios estão presentes.
- A categoria é válida e única.
- O exemplo é executável conceitualmente e os testes cobrem o comportamento relevante.

## Efeitos colaterais

Nenhum durante o planejamento. A criação ou alteração de arquivos deve seguir a política de confirmação definida em AGENTS.md.

## Exemplo

Para criar uma skill de consulta de documentação:

- Entrada: pergunta sobre uma regra interna e o caminho da documentação.
- Ação: localizar a fonte, resumir a regra e citar o caminho consultado.
- Saída: resposta com a regra, a fonte e uma indicação de incerteza quando houver.

## Testes recomendados

- Caminho principal: a skill tem frontmatter válido, todos os campos e um exemplo coerente.
- Erro ou limite: frontmatter ausente, name divergente ou categoria inválida são rejeitados.
- Efeito colateral: uma skill que altera arquivos declara a confirmação necessária.

## Credenciais e segredos

Nunca solicitar, registrar, imprimir ou incluir em saídas:
- tokens;
- senhas;
- chaves de API;
- cookies;
- certificados privados.

Use variáveis de ambiente, gerenciadores de segredo ou autenticação
interativa. Mascare qualquer valor sensível que apareça na saída.