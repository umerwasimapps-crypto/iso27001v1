"""CrewAI tool that retrieves ISO 27001 knowledge snippets from Chroma."""

from __future__ import annotations

from typing import Type

import chromadb
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from iso27001.knowledge.rag_loader import (
    COLLECTION_NAME,
    VECTOR_DB_DIR,
)


class ISOKnowledgeRetrieverInput(BaseModel):
    """Schema for queries to the knowledge retriever."""

    question: str = Field(
        ..., description="Natural-language question about ISO27001 or Annex A controls"
    )


class ISOKnowledgeRetriever(BaseTool):
    name: str = "ISOKnowledgeRetriever"
    description: str = (
        "Queries the ISO27001 knowledge base and returns the most relevant clauses or controls."
    )
    args_schema: Type[BaseModel] = ISOKnowledgeRetrieverInput

    top_k: int = 3

    def _run(self, question: str) -> str:
        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        collection = client.get_collection(name=COLLECTION_NAME)
        results = collection.query(query_texts=[question], n_results=self.top_k)

        documents = results.get("documents", [[]])[0]
        metadata = results.get("metadatas", [[]])[0]

        if not documents:
            return "No knowledge snippets found for the provided query."

        formatted = []
        for doc, meta in zip(documents, metadata):
            source = meta.get("source", "unknown")
            chunk_idx = meta.get("chunk")
            formatted.append(
                f"Source: {source} (chunk {chunk_idx})\nSnippet: {doc}"
            )
        return "\n\n".join(formatted)
