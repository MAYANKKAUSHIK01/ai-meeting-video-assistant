"""
core/llm.py — Shared LLM factory.

Centralises ChatMistralAI instantiation so that model name, API key,
and temperature are never scattered across multiple files.
"""

from __future__ import annotations

from langchain_mistralai import ChatMistralAI

from config import MISTRAL_API_KEY, MISTRAL_MODEL


def get_llm(temperature: float = 0.3) -> ChatMistralAI:
    """
    Return a configured ChatMistralAI instance.

    Args:
        temperature: Sampling temperature (0 = deterministic, 1 = creative).

    Returns:
        A ready-to-use ChatMistralAI chat model.
    """
    if not MISTRAL_API_KEY:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Add it to your .env file or environment."
        )
    return ChatMistralAI(
        model=MISTRAL_MODEL,
        mistral_api_key=MISTRAL_API_KEY,
        temperature=temperature,
    )
