"""Knowledge base: synthetic Markdown documents, masked, in an `InMemoryVectorStore` saved to a file.

- Each file of `data/knowledge/` starts with a metadata block (`kind`, `company`, `title`)
  between `---` lines and is split into chunks by `##` headings, with a size limit (the text
  before the first `##` is not indexed).
- The chunk text is masked (`masking.mask` with `[masking] names`) BEFORE the embeddings; the
  query too. The index keeps only the masked text.
- `job-search-agent index` builds the index with the configured embeddings (OpenAI) and saves it to
  `data/local/knowledge_index.json`; the app loads it at start.
- `search_knowledge` returns up to 4 chunks above `MIN_SCORE`, each with `source`, `heading` and a
  ready `citation`; with nothing above it, `note: "sem base suficiente"`.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.tools import BaseTool, tool
from langchain_core.vectorstores import InMemoryVectorStore

from job_search_agent.config import PROJECT_ROOT
from job_search_agent.masking import mask

KINDS = ("company_note", "job_description", "interview_note", "case", "strategy")
MAX_CHUNK_CHARS = 1500
TOP_K = 4
# Minimum cosine similarity for a chunk to count as a basis for the answer. Initial value for
# text-embedding-3-small, to be checked in the first real run (task 10).
MIN_SCORE = 0.30
NO_BASIS = "sem base suficiente"

HEADING = re.compile(r"^## +(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    source: str
    heading: str
    kind: str
    company: str
    title: str
    text: str


def parse_document(text: str) -> tuple[dict[str, str], str]:
    """Split the `---` metadata block (`key: value` lines) from the Markdown body."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---" or "---" not in (line.strip() for line in lines[1:]):
        raise ValueError("document must start with a metadata block between '---' lines")
    end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    metadata = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip()
    return metadata, "\n".join(lines[end + 1 :])


def _pieces(body: str) -> list[str]:
    """Paragraphs grouped up to MAX_CHUNK_CHARS (a longer paragraph stays whole)."""
    pieces, current = [], ""
    for paragraph in (p.strip() for p in body.split("\n\n")):
        if not paragraph:
            continue
        if current and len(current) + len(paragraph) + 2 > MAX_CHUNK_CHARS:
            pieces.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    return pieces + ([current] if current else [])


def split_document(path: Path, root: Path = PROJECT_ROOT) -> list[Chunk]:
    metadata, body = parse_document(path.read_text(encoding="utf-8"))
    kind, title = metadata.get("kind", ""), metadata.get("title", "")
    if kind not in KINDS or not title:
        raise ValueError(f"{path.name}: metadata needs kind (one of {KINDS}) and title")
    try:
        source = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        source = path.name
    # Only "##" sections are indexed; the text before the first one (title and the "synthetic"
    # notice) is not a basis for answers.
    parts = HEADING.split(body)
    sections = zip(parts[1::2], parts[2::2])
    return [
        Chunk(source, heading, kind, metadata.get("company", ""), title, piece)
        for heading, section in sections
        for piece in _pieces(section)
    ]


def load_chunks(directory: Path, root: Path = PROJECT_ROOT) -> list[Chunk]:
    return [
        chunk for path in sorted(directory.glob("*.md")) for chunk in split_document(path, root)
    ]


def to_document(chunk: Chunk, names: tuple[str, ...]) -> Document:
    """The masked text that goes to the embeddings and to the index."""
    text = mask(f"{chunk.title}\n## {chunk.heading}\n{chunk.text}", names)
    return Document(
        page_content=text,
        metadata={
            "source": chunk.source,
            "heading": chunk.heading,
            "kind": chunk.kind,
            "company": chunk.company,
        },
    )


def build_index(
    directory: Path, embeddings: Embeddings, names: tuple[str, ...], root: Path = PROJECT_ROOT
) -> InMemoryVectorStore:
    chunks = load_chunks(directory, root)
    if not chunks:
        raise FileNotFoundError(f"No Markdown document in {directory}")
    store = InMemoryVectorStore(embeddings)
    store.add_documents(
        [to_document(chunk, names) for chunk in chunks],
        ids=[f"{chunk.source}#{n}" for n, chunk in enumerate(chunks)],
    )
    return store


def save_index(store: InMemoryVectorStore, path: Path) -> None:
    store.dump(str(path))


def load_index(path: Path, embeddings: Embeddings) -> InMemoryVectorStore:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Knowledge index not found: {path}. Run `job-search-agent index` first."
        )
    return InMemoryVectorStore.load(str(path), embeddings)


def search(
    store: InMemoryVectorStore,
    query: str,
    names: tuple[str, ...] = (),
    kind: str | None = None,
    min_score: float = MIN_SCORE,
) -> dict[str, Any]:
    """Up to TOP_K chunks above `min_score`; none means "sem base suficiente"."""
    found = store.similarity_search_with_score(
        mask(query, names),
        k=TOP_K,
        filter=(lambda document: document.metadata["kind"] == kind) if kind else None,
    )
    results = [
        {
            "source": document.metadata["source"],
            "heading": document.metadata["heading"],
            "kind": document.metadata["kind"],
            "citation": f"[fonte: {document.metadata['source']} § {document.metadata['heading']}]",
            "score": round(score, 3),
            "text": document.page_content,
        }
        for document, score in found
        if score >= min_score
    ]
    return {"results": results} if results else {"results": [], "note": NO_BASIS}


def knowledge_tool(
    store: InMemoryVectorStore, names: tuple[str, ...] = (), min_score: float = MIN_SCORE
) -> BaseTool:
    """The `search_knowledge` tool given to the agents."""

    @tool
    def search_knowledge(query: str, kind: str | None = None) -> dict[str, Any]:
        """Search the personal knowledge base (company notes, job descriptions, interview notes,
        STAR cases and career strategy). Optional `kind`: company_note, job_description,
        interview_note, case or strategy. Cite each chunk used with its `citation`. If the
        result has the note "sem base suficiente", say so instead of completing the answer."""
        if kind is not None and kind not in KINDS:
            return {"error": "invalid_kind", "detail": f"kind must be one of {KINDS}"}
        return search(store, query, names, kind, min_score)

    return search_knowledge
