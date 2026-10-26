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

- [x] Teste com embeddings simuladas: indexar, gravar, recarregar e buscar devolve `source` e `heading`.
- [x] Teste: um nome da lista `[masking] names` e um e-mail no documento não aparecem no texto enviado aos embeddings.
- [x] Teste: consulta sem relação devolve "sem base suficiente".
- [x] Busca nos documentos versionados não encontra e-mail, telefone ou CPF.

## Validação

Executada em 2026-10-25, Windows 11, `.venv` com Python 3.12 (versões da tarefa 01, sem mudança). Sem chave da OpenAI: tudo foi verificado com embeddings simuladas; a indexação real fica pendente (ver "Pendências").

**Documentos** (`data/knowledge/`, 12 arquivos sintéticos, 42 trechos), coerentes com `data/demo/`:

| Tipo (`kind`) | Arquivos |
|---|---|
| `company_note` | `empresa-banco-aurora.md`, `empresa-transportadora-pampa.md`, `empresa-usina-solaris.md` |
| `job_description` | `vaga-banco-aurora-data-engineer.md`, `vaga-financeira-colibri-data-scientist.md`, `vaga-transportadora-pampa-ml-engineer.md` |
| `interview_note` | `entrevistas-editora-farol.md`, `entrevistas-construtora-granito.md` (etapas e feedback de `stages.csv`) |
| `case` (STAR) | `case-pipeline-incremental.md`, `case-modelo-de-churn.md`, `case-conflito-de-prioridades.md` (empresas anteriores fictícias: Distribuidora Ipê, Academia Pinhão) |
| `strategy` | `estrategia-de-carreira.md` |

Cada arquivo começa com o bloco `---` / `kind`, `company`, `title` / `---` e avisa que é sintético. As notas de empresa citam dois nomes fictícios do seed (Ana Exemplo e Carla Fictícia) de propósito, para a demonstração mostrar o mascaramento (`[pessoa]` no índice). A pergunta "o que eu anotei sobre a cultura do Banco Aurora?" tem resposta em `empresa-banco-aurora.md § Cultura e jeito de trabalhar`.

**`InMemoryVectorStore.dump` e `load` (langchain-core 1.7.0)**, conferidos com `inspect`: `dump(self, path: str) -> None` grava `dumpd(self.store)` em JSON (cria a pasta) e `load(cls, path: str, embedding: Embeddings, **kwargs)` relê com `allowed_objects=[Document]` e devolve a loja com a `embedding` dada. Servem; a alternativa do plano não foi necessária.

**Implementação** (`src/job_search_agent/knowledge.py`):

- Divisão por cabeçalho `##`; seção acima de 1.500 caracteres é dividida por parágrafos. O texto antes do primeiro `##` (título e aviso de dado sintético) não é indexado: nos testes, esse trecho curto e sem conteúdo ficava à frente dos trechos úteis.
- Texto do trecho = título do documento + título da seção + corpo, **mascarado** com `[masking] names` antes de ir aos embeddings; a consulta também é mascarada. O índice guarda só o texto mascarado, com `source` (caminho relativo, `data/knowledge/...`), `heading`, `kind` e `company`. Ids estáveis `source#n`.
- `build_index`, `save_index` (`dump` em `data/local/knowledge_index.json`), `load_index` (sem arquivo: mensagem pedindo `job-search-agent index`).
- `search(store, query, names, kind?, min_score)` e a ferramenta `search_knowledge(query, kind?)` (`knowledge_tool(store, names)`): até 4 trechos com `score >= MIN_SCORE`, cada um com `source`, `heading`, `kind`, `score`, `text` e `citation` pronta no formato do plano (`[fonte: data/knowledge/arquivo.md § título]`); nada acima do limiar: `{"results": [], "note": "sem base suficiente"}`; `kind` desconhecido: `{"error": "invalid_kind", ...}`.
- `job-search-agent index` (`cli.py`): lê a configuração, exige `OPENAI_API_KEY` (sem ela sai com código 2, sem chamar nada), indexa com `llm.embeddings(config)` e grava o índice. Tokens dos embeddings não são estimados (a resposta da API de embeddings via LangChain não traz uso), como prevê o plano.

**Decisões**

- `MIN_SCORE = 0.30` (similaridade de cosseno) é um valor inicial para `text-embedding-3-small`, constante em `knowledge.py` e parâmetro de `search`/`knowledge_tool`; a calibragem fica para a primeira execução real.
- Os testes usam `LexicalEmbeddings` (saco de palavras com hash SHA-256 em 512 dimensões, determinístico, em `tests/test_knowledge.py`) com limiar próprio de 0,15. Ela só garante que o trecho certo é recuperado, não que vem em primeiro; por isso o teste da cultura do Banco Aurora procura o trecho entre os resultados.
- O cache versionado de embeddings dos textos sintéticos em `evals/agent/fixtures/` não foi criado: precisa da chave para gerar vetores reais e é usado pela avaliação (tarefas 09 e 10).

**Testes** (`tests/test_knowledge.py`, 9 testes novos):

- documentos versionados válidos (8 a 15 arquivos, todos os `kind`, `source` relativo);
- indexar com embeddings simuladas, gravar com `dump`, recarregar com `load` e buscar a cultura do Banco Aurora: trecho com `source`, `heading` e `citation` esperados, nome do seed mascarado;
- filtro por `kind`; ferramenta `search_knowledge` (nome, resultado e `kind` inválido);
- consulta sem relação ("receita de bolo de cenoura...") devolve `{"results": [], "note": "sem base suficiente"}`;
- um documento temporário com nome da lista em maiúsculas, nome sem acento, e-mail e telefone: os textos recebidos pelas embeddings (documentos e consulta) têm `[pessoa]` e `[email]` e não têm nenhum desses dados; o índice também não;
- nenhum documento versionado casa com os padrões de e-mail, telefone, CPF ou link de perfil de `masking.py`;
- `job-search-agent index` sem chave sai com código 2 e não grava índice; índice ausente explica o que fazer.

```text
.venv\Scripts\python.exe tools/scripts/lint_and_tests.py --strict   -> 67 passed; ruff limpo; validação estrita sem falhas
.venv\Scripts\python.exe -m ruff format --check src tests          -> 18 files already formatted
grep -rEn '<e-mail>|<telefone>|<CPF>|linkedin\.com' data/knowledge  -> nenhuma ocorrência
```

**Pendências**

- Rodar `job-search-agent index` com a chave do autor e conferir a busca real (incluindo o limiar `MIN_SCORE`) — tarefa 10.
- Cache de embeddings dos textos sintéticos em `evals/agent/fixtures/` para a avaliação sem chave — tarefas 09 e 10.

## Status

```text
concluída (indexação real com a API pendente da chave do autor)
```
