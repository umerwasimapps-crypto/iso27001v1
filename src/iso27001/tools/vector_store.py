"""Utility for building a Chroma vector store from the ISO 27001 knowledge base."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
COLLECTION_NAME = "iso27001_knowledge"
EMBEDDING_MODEL = os.environ.get("HUGGINGFACE_EMBEDDING_MODEL", "BAAI/bge-m3")


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 40) -> List[str]:
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start = max(end - overlap, 0)
    return chunks


def _load_documents() -> Iterable[tuple[str, str, dict]]:
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        chunks = _chunk_text(content)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{path.stem}-{idx}"
            metadata = {"source": path.name, "chunk": idx}
            yield doc_id, chunk, metadata


def build_vector_store() -> None:
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        # Collection may not exist yet; ignore errors to allow creation.
        pass

    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
    )
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    documents = list(_load_documents())
    if not documents:
        raise FileNotFoundError(
            f"No markdown files found in {KNOWLEDGE_BASE_DIR}. Add knowledge sources before building the store."
        )

    ids, texts, metadatas = zip(*documents)
    collection.add(ids=list(ids), documents=list(texts), metadatas=list(metadatas))

    print(f"Loaded {len(documents)} chunks into collection '{COLLECTION_NAME}' at {VECTOR_DB_DIR}.")


if __name__ == "__main__":
    build_vector_store()
