"""Knowledge base with simulated embeddings (no network): index, save, load, search and masking."""

import hashlib
import math
import re
import tomllib
from pathlib import Path

import pytest
from langchain_core.embeddings import Embeddings

from job_search_agent import cli
from job_search_agent.config import PROJECT_ROOT, parse_config
from job_search_agent.knowledge import (
    KINDS,
    NO_BASIS,
    build_index,
    knowledge_tool,
    load_chunks,
    load_index,
    save_index,
    search,
)
from job_search_agent.masking import CPF, EMAIL, PHONE, PROFILE, fold

KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"
NAMES = ("Ana Exemplo", "Carla Fictícia")
# Threshold for the lexical embeddings below (the real one, MIN_SCORE, is for OpenAI).
TEST_MIN_SCORE = 0.15


class LexicalEmbeddings(Embeddings):
    """Deterministic bag of words (words of 4+ letters, without accents) hashed into 512
    dimensions. It records every text it receives, to check what would go to the provider."""

    def __init__(self) -> None:
        self.received: list[str] = []

    def _vector(self, text: str) -> list[float]:
        self.received.append(text)
        vector = [0.0] * 512
        for word in re.findall(r"\w{4,}", fold(text)):
            vector[int(hashlib.sha256(word.encode()).hexdigest(), 16) % 512] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


@pytest.fixture(scope="module")
def index_path(tmp_path_factory) -> Path:
    path = tmp_path_factory.mktemp("knowledge") / "knowledge_index.json"
    save_index(build_index(KNOWLEDGE_DIR, LexicalEmbeddings(), NAMES), path)
    return path


@pytest.fixture
def store(index_path: Path):
    return load_index(index_path, LexicalEmbeddings())


def test_versioned_documents_are_valid() -> None:
    files = sorted(KNOWLEDGE_DIR.glob("*.md"))
    assert 8 <= len(files) <= 15
    chunks = load_chunks(KNOWLEDGE_DIR)
    assert {chunk.kind for chunk in chunks} == set(KINDS)
    assert {chunk.source for chunk in chunks} == {f"data/knowledge/{f.name}" for f in files}


def test_saved_index_is_reloaded_and_search_cites_source_and_heading(store) -> None:
    answer = search(
        store,
        "O que eu anotei sobre a cultura do Banco Aurora?",
        NAMES,
        min_score=TEST_MIN_SCORE,
    )
    assert 1 <= len(answer["results"]) <= 4
    assert all(result["source"] and result["heading"] for result in answer["results"])
    # The lexical embeddings only promise that the chunk is retrieved, not that it is first.
    culture = next(r for r in answer["results"] if r["heading"] == "Cultura e jeito de trabalhar")
    assert culture["source"] == "data/knowledge/empresa-banco-aurora.md"
    assert culture["citation"] == (
        "[fonte: data/knowledge/empresa-banco-aurora.md § Cultura e jeito de trabalhar]"
    )
    assert "Squads pequenos" in culture["text"]
    assert "[pessoa]" in culture["text"] and "Ana Exemplo" not in culture["text"]


def test_kind_filter(store) -> None:
    answer = search(
        store, "entrevista técnica streaming", kind="interview_note", min_score=TEST_MIN_SCORE
    )
    assert answer["results"]
    assert {result["kind"] for result in answer["results"]} == {"interview_note"}
    assert answer["results"][0]["source"].endswith("entrevistas-construtora-granito.md")


def test_unrelated_query_has_no_basis(store) -> None:
    answer = search(
        store, "receita de bolo de cenoura com cobertura de chocolate", min_score=TEST_MIN_SCORE
    )
    assert answer == {"results": [], "note": NO_BASIS}


def test_tool_returns_results_and_refuses_unknown_kind(store) -> None:
    search_knowledge = knowledge_tool(store, NAMES, min_score=TEST_MIN_SCORE)
    assert search_knowledge.name == "search_knowledge"
    result = search_knowledge.invoke({"query": "case de conflito de prioridades", "kind": "case"})
    assert result["results"][0]["source"].endswith("case-conflito-de-prioridades.md")
    assert search_knowledge.invoke({"query": "x", "kind": "salary"})["error"] == "invalid_kind"


def test_names_and_email_do_not_reach_the_embeddings(tmp_path: Path) -> None:
    directory = tmp_path / "data" / "knowledge"
    directory.mkdir(parents=True)
    (directory / "nota.md").write_text(
        "---\nkind: interview_note\ncompany: Banco Aurora\ntitle: Nota\n---\n\n"
        "## Conversa\n\nFalei com ANA EXEMPLO (ana.exemplo@example.com, 11 91234-5678) "
        "e com Carla Ficticia sobre o Banco Aurora.\n",
        encoding="utf-8",
    )
    (directory / "outra.md").write_text(
        "---\nkind: interview_note\ncompany: Banco Aurora\ntitle: Outra\n---\n\n"
        "## Retorno de Carla Fictícia (carla@example.com)\n\nRetorno positivo do Banco Aurora.\n",
        encoding="utf-8",
    )
    embeddings = LexicalEmbeddings()
    store = build_index(directory, embeddings, NAMES, root=tmp_path)
    found = search(store, "o que a Ana Exemplo disse? ana.exemplo@example.com", NAMES, min_score=0)
    feedback = search(store, "retorno positivo", NAMES, min_score=0)["results"]
    assert found["results"] and feedback

    sent = "\n".join(embeddings.received)
    assert "[pessoa]" in sent and "[email]" in sent and "Banco Aurora" in sent
    personal_data = ("ANA EXEMPLO", "Ana Exemplo", "Carla Fic", "@example.com", "91234")
    for personal in personal_data:
        assert personal not in sent
    stored = {document["metadata"]["source"]: document for document in store.store.values()}
    assert set(stored) == {"data/knowledge/nota.md", "data/knowledge/outra.md"}
    assert (
        stored["data/knowledge/outra.md"]["metadata"]["heading"] == "Retorno de [pessoa] ([email])"
    )
    assert "ANA EXEMPLO" not in stored["data/knowledge/nota.md"]["text"]

    # The citation given to the model and the saved index file have no name or e-mail either.
    citations = [result["citation"] for result in found["results"] + feedback]
    assert "[fonte: data/knowledge/outra.md § Retorno de [pessoa] ([email])]" in citations
    index_file = tmp_path / "knowledge_index.json"
    save_index(store, index_file)
    saved = index_file.read_text(encoding="utf-8")
    assert "[pessoa]" in saved and "[email]" in saved
    for personal in (*personal_data, "Carla Fict\\u00edcia"):
        assert personal not in saved
    for result in found["results"] + feedback:
        assert all(personal not in str(result) for personal in personal_data)


def test_versioned_documents_have_no_email_phone_or_cpf() -> None:
    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for pattern in (EMAIL, PHONE, CPF, PROFILE):
            assert not pattern.search(text), (path.name, pattern.pattern)


def test_index_command_without_key_does_not_call(tmp_path: Path, monkeypatch, capsys) -> None:
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    monkeypatch.setattr(cli, "load_config", lambda: parse_config(data, root=tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert cli.main(["index"]) == 2
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().err
    assert not (tmp_path / "data" / "local" / "knowledge_index.json").exists()


def test_index_command_reports_unknown_embedding_tokens(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    config = parse_config(data, root=tmp_path)
    config.knowledge_dir.mkdir(parents=True)
    source = KNOWLEDGE_DIR / "empresa-banco-aurora.md"
    (config.knowledge_dir / source.name).write_text(source.read_text(encoding="utf-8"), "utf-8")
    monkeypatch.setattr(cli, "load_config", lambda: config)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    monkeypatch.setattr("job_search_agent.llm.embeddings", lambda _config: LexicalEmbeddings())
    assert cli.main(["index"]) == 0
    assert "tokens de embeddings: desconhecidos" in capsys.readouterr().out
    assert config.knowledge_index.exists()


def test_missing_index_explains_what_to_do(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="job-search-agent index"):
        load_index(tmp_path / "knowledge_index.json", LexicalEmbeddings())
