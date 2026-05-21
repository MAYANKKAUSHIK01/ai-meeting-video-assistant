"""
core/vector_store.py — ChromaDB vector store construction and retrieval.

Manages the local persistent vector store used by the RAG pipeline.
Embedding model is loaded lazily and reused via a module-level cache to
avoid expensive re-downloads between pipeline runs.
"""

from __future__ import annotations

import logging

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    RAG_CHUNK_OVERLAP,
    RAG_CHUNK_SIZE,
    RAG_TOP_K,
    VECTOR_DB_DIR,
)

logger = logging.getLogger(__name__)

# ── Embedding singleton ───────────────────────────────────────────────────────
_embeddings: HuggingFaceEmbeddings | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Return (or create) the cached HuggingFace embedding function."""
    global _embeddings
    if _embeddings is None:
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading embedding model '%s' on '%s'…", EMBEDDING_MODEL, device)
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": device},
        )
        logger.info("Embedding model ready.")
    return _embeddings


# ── Public API ────────────────────────────────────────────────────────────────

def build_vector_store(transcript: str) -> Chroma:
    """
    Chunk the transcript, embed each chunk, and persist to ChromaDB.

    A fresh collection is written on every call (old data is replaced by
    Chroma's upsert behaviour when the same collection name is reused).

    Args:
        transcript: Full plain-text meeting transcript.

    Returns:
        A Chroma vector store ready for similarity search.
    """
    logger.info("Building vector store…")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )
    texts = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata={"chunk_index": i})
        for i, chunk in enumerate(texts)
    ]

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=_get_embeddings(),
        collection_name=CHROMA_COLLECTION,
        persist_directory=VECTOR_DB_DIR,
    )

    logger.info("Vector store built with %d document(s).", len(docs))
    return vector_store


def load_vector_store() -> Chroma:
    """
    Load an existing persisted ChromaDB collection.

    Use this to reload the store across process restarts without
    re-embedding the transcript.

    Returns:
        The persisted Chroma vector store.
    """
    logger.info("Loading persisted vector store from '%s'…", VECTOR_DB_DIR)
    return Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=_get_embeddings(),
        persist_directory=VECTOR_DB_DIR,
    )


def get_retriever(vector_store: Chroma, k: int = RAG_TOP_K):
    """
    Wrap a Chroma store as a LangChain retriever.

    Args:
        vector_store: An initialised Chroma instance.
        k:            Number of documents to return per query.

    Returns:
        A LangChain BaseRetriever.
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
