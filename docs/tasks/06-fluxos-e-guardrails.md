# Tarefa: fluxos e guardrails

## Objetivo

Escrever as instruções do roteador, dos agentes e dos cinco fluxos (rodada diária, registrar fato, avaliar vaga, redigir mensagem, preparar entrevista), com as regras da decisão 0002 e a citação de fonte.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Grafo" (fluxos e regras) e "Guardrails"; [decisão 0002](../architecture/decisions/0002-acoes-externas-ficam-com-a-pessoa.md). Casos de uso 1 a 5 da especificação.

## Pré-condições

Tarefa 05 concluída.

## Arquivos prováveis

`src/job_search_agent/prompts.py`, `tests/test_prompts.py`.

## Passos

1. Instruções do roteador com exemplos de cada rota, inclusive os quatro pedidos de recusa do plano.
2. Instruções comuns: não inventar status, datas ou valores; fatos do servidor; texto redigido é para a pessoa enviar; nunca dizer que enviou; honestidade de autoria; discrição entre contatos; `source` = origem do estado; formato de citação.
3. Instruções de cada fluxo, anexadas ao agente responsável; rodada diária com no máximo cinco ações e sem escrita.
4. Respostas fixas de `decline` (recusa com o que a pessoa pode fazer; fora do escopo).

## Critérios de conclusão

- [ ] Teste: cada regra da decisão 0002 aparece nas instruções comuns dos dois agentes.
- [ ] Teste: as respostas de `decline` não prometem envio nem ação externa.
- [ ] Verificação manual curta com modelo real (fora do CI) de um caso de cada fluxo, anotada aqui; a evidência formal fica na tarefa 09.

## Validação

A preencher.

## Status

```text
pendente
```
