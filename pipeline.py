"""
pipeline.py — Core orchestration logic for the LENS meeting intelligence pipeline.

This module is UI-agnostic: it can be called from the Streamlit app (app.py),
the CLI entry point (main.py), or a test script, without any coupling to
Streamlit-specific state.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import generate_title, summarize
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain

logger = logging.getLogger(__name__)


def run_pipeline(
    source: str,
    language: str = "english",
    on_step: callable | None = None,
) -> dict:
    """
    Run the full LENS analysis pipeline end-to-end.

    Args:
        source:   YouTube URL or absolute/relative path to a local media file.
        language: Transcription language — "english" (Whisper) or "hinglish" (Sarvam).
        on_step:  Optional callback invoked as on_step(step_key, state) where
                  state is "active" | "done" | "failed". Used by the Streamlit
                  UI to update the progress sidebar without coupling this module
                  to Streamlit.

    Returns:
        A dict with keys:
            title, transcript, summary,
            action_items, key_decisions, open_questions, rag_chain
    """

    def _tick(key: str, state: str) -> None:
        if on_step:
            on_step(key, state)

    # ── Step 1: Audio acquisition ─────────────────────────────────────────────
    _tick("audio", "active")
    chunks = process_input(source)
    _tick("audio", "done")

    # ── Step 2: Transcription ─────────────────────────────────────────────────
    _tick("transcript", "active")
    transcript = transcribe_all(chunks, language)
    logger.info("Transcript preview: %s…", transcript[:200])
    _tick("transcript", "done")

    # ── Step 3: Title generation ──────────────────────────────────────────────
    _tick("title", "active")
    title = generate_title(transcript)
    _tick("title", "done")

    # ── Step 4: Summarisation ─────────────────────────────────────────────────
    _tick("summary", "active")
    summary = summarize(transcript)
    _tick("summary", "done")

    # ── Step 5: Parallel extraction ───────────────────────────────────────────
    _tick("extract", "active")
    with ThreadPoolExecutor(max_workers=3) as pool:
        fa = pool.submit(extract_action_items, transcript)
        fd = pool.submit(extract_key_decisions, transcript)
        fq = pool.submit(extract_questions, transcript)
        action_items = fa.result()
        key_decisions = fd.result()
        open_questions = fq.result()
    _tick("extract", "done")

    # ── Step 6: RAG engine ────────────────────────────────────────────────────
    _tick("rag", "active")
    rag_chain = build_rag_chain(transcript)
    _tick("rag", "done")

    logger.info("Pipeline complete — title: %s", title)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": open_questions,
        "rag_chain": rag_chain,
    }
