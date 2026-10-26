# Tarefa: avaliação

## Objetivo

Versionar 20 casos de avaliação e o executor com as métricas de roteamento, ferramentas, argumentos, propostas, recusa, recuperação e fidelidade, rodando no CI com modelo simulado e sem chave.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seções "Avaliação" e "Guardrails". Critérios da especificação: "a avaliação roda no CI sem chave de API"; "a avaliação do conhecimento reporta acerto na recuperação e fidelidade à fonte"; requisito "quando faltar dado, pergunta".

## Pré-condições

Tarefas 04 a 07 concluídas.

## Arquivos prováveis

`evals/agent/cases.toml`, `evals/agent/fixtures/`, `src/job_search_agent/evals.py`, `tests/test_evals.py`, `.github/workflows/validate.yml` (passo da avaliação simulada).

## Passos

1. Escrever os 20 casos (4 Network, 5 Vagas, 4 conhecimento, 4 recusa, 1 fora do escopo, 2 dado faltante) com os campos do plano, sobre os dados de demonstração (`data/demo`) e `reference_date = "2026-03-16"`; `expected_args` das ferramentas de data incluem essa data.
2. Roteiros do modelo simulado por caso e cache de embeddings dos documentos sintéticos e das consultas dos casos.
3. `evals.py`: sobe o servidor num banco temporário criado com os dados de `data/demo` (como `create_demo_db`), roda cada caso pelo grafo, calcula as métricas e imprime uma tabela; `--real` usa os modelos configurados e grava `evals/agent/results/<data>-<modelo>.md`.
4. Fidelidade = toda citação da resposta está entre os trechos recuperados no turno (sem juiz por modelo).
5. Passo no CI: `python -m job_search_agent.evals` sem `OPENAI_API_KEY`, falhando se alguma métrica do harness cair abaixo de 100%.

## Critérios de conclusão

- [ ] 20 casos versionados, incluindo os quatro pedidos de recusa da decisão 0002 e os dois de dado faltante (nenhuma proposta e uma pergunta).
- [ ] Avaliação simulada passa no CI sem chave.
- [ ] O relatório mostra recuperação (`hit@4`) e fidelidade (citações entre os trechos recuperados).
- [ ] Teste: um caso com ferramenta errada, ou com proposta onde não devia haver, é contado como erro (o executor não aprova tudo).

## Validação

A preencher.

## Status

```text
pendente
```
