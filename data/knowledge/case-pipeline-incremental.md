---
kind: case
company: Distribuidora Ipê
title: Case: pipeline incremental na Distribuidora Ipê
---

# Case: pipeline incremental na Distribuidora Ipê

Case fictício de demonstração, no formato STAR, para preparar entrevistas.

## Situação

A carga noturna de vendas da Distribuidora Ipê reprocessava a base inteira todos os dias e levava seis horas. Quando falhava, os relatórios da manhã ficavam sem dados e a área comercial decidia às cegas.

## Tarefa

Reduzir o tempo da carga e tornar o reprocessamento seguro, sem parar os relatórios existentes.

## Ação

- Troquei a carga completa por processamento incremental, com marca d'água por data de atualização.
- Criei testes de qualidade de dados (contagem, unicidade e paridade com o sistema de origem) que barram a publicação quando falham.
- Tornei cada etapa idempotente, para que o reprocessamento de um dia não duplicasse vendas.
- Documentei a decisão num registro curto e apresentei para o time antes de mudar.

## Resultado

A carga caiu de seis horas para quarenta minutos; as falhas passaram a ser detectadas antes da publicação, e o reprocessamento de um dia virou um comando. Serve para perguntas sobre qualidade de dados, migração e otimização de pipelines (por exemplo, o caso técnico do Banco Aurora).
