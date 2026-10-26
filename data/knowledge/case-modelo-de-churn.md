---
kind: case
company: Academia Pinhão
title: Case: modelo de churn na Academia Pinhão
---

# Case: modelo de churn na Academia Pinhão

Case fictício de demonstração, no formato STAR, para preparar entrevistas.

## Situação

A rede de academias Academia Pinhão perdia muitos alunos nos três primeiros meses e só percebia o cancelamento quando ele acontecia.

## Tarefa

Prever quais alunos tinham maior risco de cancelar para que as unidades fizessem contato antes.

## Ação

- Montei um modelo de classificação com frequência de treino, tempo de matrícula e uso de aulas coletivas.
- Defini com o negócio a métrica de sucesso: retenção dos alunos contatados em relação a um grupo de controle.
- Coloquei o modelo em produção como um job semanal e criei um painel de monitoramento de deriva dos dados e de desempenho.

## Resultado

Em três meses de teste controlado, a retenção do grupo contatado foi oito pontos percentuais maior. O monitoramento detectou uma deriva quando uma unidade mudou o sistema de catraca, e o modelo foi retreinado antes de perder qualidade. Serve para vagas de ciência de dados e de MLOps (Financeira Colibri e Transportadora Pampa).
