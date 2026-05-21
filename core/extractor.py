"""
core/extractor.py — Structured information extraction from meeting transcripts.

Extracts three artefact types via separate LLM calls:
  - Action items  (task, owner, deadline)
  - Key decisions (what was agreed upon)
  - Open questions (unresolved topics)

All three chains share a single build_extraction_chain() factory, removing
the duplicate chain-building code that existed in the original implementation.
"""

from __future__ import annotations

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from config import LLM_TEMP_EXTRACT
from core.llm import get_llm

logger = logging.getLogger(__name__)

# ── Prompt definitions ────────────────────────────────────────────────────────

_ACTION_ITEMS_PROMPT = (
    "You are an expert meeting analyst. From the meeting transcript, "
    "extract all action items. For each provide:\n"
    "- Task description\n"
    "- Owner (who is responsible)\n"
    "- Deadline (if mentioned, else write 'Not specified')\n\n"
    "Format as a numbered list. If none found, write 'No action items found.'"
)

_KEY_DECISIONS_PROMPT = (
    "You are an expert meeting analyst. From the meeting transcript, "
    "extract all key decisions made. Format as a numbered list. "
    "If none found, write 'No key decisions found.'"
)

_OPEN_QUESTIONS_PROMPT = (
    "From the meeting transcript, extract all unresolved questions "
    "or topics needing follow-up. Format as a numbered list. "
    "If none found, write 'No open questions found.'"
)


# ── Chain factory ─────────────────────────────────────────────────────────────

def _build_extraction_chain(system_prompt: str):
    """
    Build a reusable LCEL extraction chain for a given system instruction.

    The chain accepts a plain string (the transcript) and returns a string.
    """
    llm = get_llm(temperature=LLM_TEMP_EXTRACT)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "{text}")]
    )
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | prompt
        | llm
        | StrOutputParser()
    )


# ── Public API ────────────────────────────────────────────────────────────────

def extract_action_items(transcript: str) -> str:
    """
    Extract all action items from the transcript.

    Returns:
        A numbered-list string of action items, or 'No action items found.'
    """
    logger.info("Extracting action items…")
    return _build_extraction_chain(_ACTION_ITEMS_PROMPT).invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    """
    Extract all key decisions from the transcript.

    Returns:
        A numbered-list string of decisions, or 'No key decisions found.'
    """
    logger.info("Extracting key decisions…")
    return _build_extraction_chain(_KEY_DECISIONS_PROMPT).invoke(transcript)


def extract_questions(transcript: str) -> str:
    """
    Extract all open / unresolved questions from the transcript.

    Returns:
        A numbered-list string of questions, or 'No open questions found.'
    """
    logger.info("Extracting open questions…")
    return _build_extraction_chain(_OPEN_QUESTIONS_PROMPT).invoke(transcript)