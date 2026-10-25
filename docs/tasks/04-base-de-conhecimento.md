# Tarefa: base de conhecimento

## Objetivo

Criar os documentos sintéticos, indexá-los com mascaramento em um `InMemoryVectorStore` persistido em arquivo e oferecer a ferramenta `search_knowledge` com citação de fonte, tudo em `knowledge.py`.

## Especificação relacionada

[Plano](../specs/agente-de-carreira-plano.md), seção "RAG". Requisitos de conhecimento da especificação; Q1 (embeddings pela OpenAI, com mascaramento).

## Pré-condições

Tarefas 01 e 03 concluídas (configuração e mascaramento).

## Arquivos prováveis

`data/knowledge/*.md` (12 a 15 arquivos sintéticos), `src/job_search_agent/knowledge.py`, `src/job_search_agent/cli.py` (comando `index`), `tests/test_knowledge.py`.

## Passos

1. Escrever os documentos sintéticos (vagas e empresas do seed do servidor, notas de entrevista, cases fictícios, estratégia), com bloco de metadados. Nenhum dado real.
2. Confirmar na versão instalada as assinaturas de `InMemoryVectorStore.dump` e `load`; se não servirem, registrar e propor a alternativa do plano.
3. `knowledge.py`: divisão por cabeçalho `##`, mascaramento, embeddings, gravação em `data/local/knowledge_index.json`, carga.
4. `search_knowledge(query, kind?)`: até 4 trechos acima do limiar, com `source` e `heading`; sem resultado, `note: "sem base suficiente"`.
5. Comando `job-search-agent index`.

## Critérios de conclusão

- [ ] Teste com embeddings simuladas: indexar, gravar, recarregar e buscar devolve `source` e `heading`.
- [ ] Teste: um nome da lista `[masking] names` e um e-mail no documento não aparecem no texto enviado aos embeddings.
- [ ] Teste: consulta sem relação devolve "sem base suficiente".
- [ ] Busca nos documentos versionados não encontra e-mail, telefone ou CPF.

## Validação

A preencher.

## Status

```text
pendente
```
