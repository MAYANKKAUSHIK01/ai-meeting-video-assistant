"""
core/summarizer.py — Meeting transcript summarisation and title generation.

Uses a map-reduce strategy for long transcripts:
  1. Split transcript into overlapping chunks.
  2. Summarise each chunk concurrently (map).
  3. Combine partial summaries into a final professional summary (reduce).

Title generation takes only the first 2 000 characters to keep it cheap.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import LLM_TEMP_SUMMARY, SUMMARY_CHUNK_OVERLAP, SUMMARY_CHUNK_SIZE
from core.llm import get_llm

logger = logging.getLogger(__name__)

# ── Prompt templates ──────────────────────────────────────────────────────────

_MAP_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Summarise this portion of a meeting transcript concisely."),
        ("human", "{text}"),
    ]
)

_REDUCE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert meeting summariser. Combine these partial summaries "
            "into one final professional meeting summary in bullet points.",
        ),
        ("human", "{text}"),
    ]
)

_TITLE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Based on the meeting transcript, generate a short professional meeting title "
            "(max 8 words). Return the title only — no punctuation, no explanation.",
        ),
        ("human", "{text}"),
    ]
)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _split_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=SUMMARY_CHUNK_SIZE,
        chunk_overlap=SUMMARY_CHUNK_OVERLAP,
    )
    return splitter.split_text(transcript)


def _wrap_text(text: str) -> dict:
    """Wrap a plain string into the {text: ...} dict expected by prompts."""
    return {"text": text}


# ── Public API ────────────────────────────────────────────────────────────────

def summarize(transcript: str) -> str:
    """
    Produce a structured bullet-point summary of the full meeting transcript.

    Uses map-reduce: partial chunk summaries run concurrently, then a single
    reduce call combines them into the final output.

    Args:
        transcript: Full plain-text meeting transcript.

    Returns:
        A professional bullet-point summary string.
    """
    llm = get_llm(temperature=LLM_TEMP_SUMMARY)
    map_chain = _MAP_PROMPT | llm | StrOutputParser()

    chunks = _split_transcript(transcript)
    logger.info("Summarising %d chunk(s) concurrently…", len(chunks))

    with ThreadPoolExecutor() as pool:
        chunk_summaries = list(
            pool.map(lambda chunk: map_chain.invoke({"text": chunk}), chunks)
        )

    combined = "\n\n".join(chunk_summaries)

    reduce_chain = (
        RunnablePassthrough()
        | RunnableLambda(_wrap_text)
        | _REDUCE_PROMPT
        | llm
        | StrOutputParser()
    )

    summary = reduce_chain.invoke(combined)
    logger.info("Summary generated (%d chars).", len(summary))
    return summary


def generate_title(transcript: str) -> str:
    """
    Generate a concise meeting title (≤ 8 words) from the transcript.

    Only the first 2 000 characters are sent to reduce token usage.

    Args:
        transcript: Full plain-text meeting transcript.

    Returns:
        A short meeting title string.
    """
    llm = get_llm(temperature=LLM_TEMP_SUMMARY)

    title_chain = (
        RunnablePassthrough()
        | RunnableLambda(_wrap_text)
        | _TITLE_PROMPT
        | llm
        | StrOutputParser()
    )

    title = title_chain.invoke(transcript[:2_000])
    logger.info("Title generated: %s", title)
    return title.strip()
