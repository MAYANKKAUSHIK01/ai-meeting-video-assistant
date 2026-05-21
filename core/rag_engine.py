"""
core/rag_engine.py — Retrieval-Augmented Generation (RAG) pipeline.

Builds a LangChain LCEL chain that:
  1. Embeds the user question and retrieves the top-k most relevant transcript chunks.
  2. Passes those chunks as context to the Mistral LLM.
  3. Returns a grounded, concise answer.

The dead load_rag_chain() function (never called by the app) has been removed.
"""

from __future__ import annotations

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from config import LLM_TEMP_RAG, RAG_TOP_K
from core.llm import get_llm
from core.vector_store import build_vector_store, get_retriever

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────────────

_RAG_SYSTEM_PROMPT = """\
You are an expert meeting assistant. Answer the user's question based ONLY \
on the meeting transcript context provided below.

If the answer is not in the context, respond with:
"I could not find this information in the meeting transcript."

Be concise and precise. When quoting someone, mention it clearly.

Context from meeting transcript:
{context}"""

_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _RAG_SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_docs(docs) -> str:
    """Concatenate retrieved document page content with blank-line separators."""
    return "\n\n".join(doc.page_content for doc in docs)


# ── Public API ────────────────────────────────────────────────────────────────

def build_rag_chain(transcript: str):
    """
    Construct and return a RAG chain grounded in the provided transcript.

    The chain accepts a plain question string and returns an answer string.

    Args:
        transcript: Full plain-text meeting transcript.

    Returns:
        A LangChain LCEL Runnable (question: str → answer: str).
    """
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=RAG_TOP_K)
    llm = get_llm(temperature=LLM_TEMP_RAG)

    rag_chain = (
        {
            "context": retriever | RunnableLambda(_format_docs),
            "question": RunnablePassthrough(),
        }
        | _RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    logger.info("RAG chain ready.")
    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    """
    Invoke the RAG chain with a user question and return the answer.

    Args:
        rag_chain: A chain returned by build_rag_chain().
        question:  The user's question string.

    Returns:
        The LLM's answer as a plain string.
    """
    logger.info("RAG query: %s", question)
    answer: str = rag_chain.invoke(question)
    logger.info("RAG answer: %s", answer[:120])
    return answer
