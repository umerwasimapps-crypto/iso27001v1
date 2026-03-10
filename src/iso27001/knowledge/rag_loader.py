"""Load ISO27001 markdown knowledge files into a Chroma vector database."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
COLLECTION_NAME = "iso27001_knowledge"
DEFAULT_CHUNK_SIZE = 400
DEFAULT_CHUNK_OVERLAP = 40
EMBEDDING_MODEL = os.environ.get("HUGGINGFACE_EMBEDDING_MODEL", "BAAI/bge-m3")


@dataclass(frozen=True)
class DocumentChunk:
    """Represents a chunk of knowledge ready for embedding."""

    doc_id: str
    text: str
    metadata: dict


def read_markdown_files(directory: Path = KNOWLEDGE_BASE_DIR) -> Iterable[tuple[Path, str]]:
    """Yield (path, content) tuples for every markdown file in the knowledge base."""
    for path in sorted(directory.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if content:
            yield path, content


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[str]:
    """Split text into word-based chunks suitable for embedding."""
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


def generate_chunks() -> List[DocumentChunk]:
    """Create DocumentChunk objects for every markdown file in the knowledge base."""
    chunks: List[DocumentChunk] = []
    for path, content in read_markdown_files():
        for idx, chunk in enumerate(chunk_text(content)):
            chunks.append(
                DocumentChunk(
                    doc_id=f"{path.stem}-{idx}",
                    text=chunk,
                    metadata={"source": path.name, "chunk": idx},
                )
            )
    return chunks


def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """Generate vector embeddings using a Hugging Face sentence transformer."""
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return embedding_fn(list(texts))


def store_embeddings(chunks: List[DocumentChunk]) -> None:
    """Persist embeddings and metadata into the Chroma database."""
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,
    )

    embeddings = embed_texts([chunk.text for chunk in chunks])
    collection.add(
        ids=[chunk.doc_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
        embeddings=embeddings,
    )


def ingest_knowledge_base() -> Tuple[int, Path]:
    """Read, chunk, embed, and store all knowledge base markdown files."""
    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(f"Knowledge base folder not found: {KNOWLEDGE_BASE_DIR}")

    chunks = generate_chunks()
    if not chunks:
        raise FileNotFoundError(
            f"No markdown documents found in {KNOWLEDGE_BASE_DIR}. Add files before ingestion."
        )

    store_embeddings(chunks)
    return len(chunks), VECTOR_DB_DIR


if __name__ == "__main__":
    total_chunks, vector_path = ingest_knowledge_base()
    print(f"Loaded {total_chunks} chunks into {vector_path / COLLECTION_NAME}.")
