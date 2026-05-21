"""
core/transcriber.py — Speech-to-text transcription engine.

Supports two backends:
  - Whisper (local GPU/CPU)  — used for "english"
  - Sarvam AI (cloud API)    — used for "hinglish" (translates to English)

Key design decisions:
  - Whisper model is loaded lazily and cached in a module-level singleton to
    avoid reloading the model between calls in the same process.
  - Sarvam API rejects audio > 30 s; chunks are sliced into SARVAM_PIECE_SECONDS
    pieces before upload and cleaned up in a finally block.
  - Sarvam calls are I/O-bound and run concurrently; Whisper calls are CPU/GPU-
    bound and run sequentially (the model is not thread-safe).
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from pydub import AudioSegment

from config import (
    SARVAM_API_KEY,
    SARVAM_MAX_WORKERS,
    SARVAM_PIECE_SECONDS,
    SARVAM_STT_MODEL,
    SARVAM_STT_URL,
    WHISPER_MODEL,
)

logger = logging.getLogger(__name__)

# ── Whisper singleton ─────────────────────────────────────────────────────────
_whisper_model = None


def _load_whisper_model():
    """Load (or return cached) Whisper model onto the best available device."""
    global _whisper_model
    if _whisper_model is None:
        import torch
        import whisper

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading Whisper model '%s' on device '%s'…", WHISPER_MODEL, device)
        _whisper_model = whisper.load_model(WHISPER_MODEL, device=device)
        logger.info("Whisper model ready.")
    return _whisper_model


# ── Whisper backend ───────────────────────────────────────────────────────────

def _transcribe_with_whisper(chunk_path: str) -> str:
    """Transcribe a single WAV chunk using the local Whisper model."""
    import torch

    model = _load_whisper_model()
    use_fp16 = torch.cuda.is_available()

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        fp16=use_fp16,                     # 2× faster on GPU
        beam_size=1,                       # greedy — fastest decoding
        best_of=1,
        condition_on_previous_text=False,  # no cross-chunk context leak
        no_speech_threshold=0.6,           # fast-skip silent segments
        compression_ratio_threshold=2.4,
    )
    return result["text"].strip()


# ── Sarvam backend ────────────────────────────────────────────────────────────

def _post_piece_to_sarvam(piece_path: str) -> str:
    """Send one ≤ 30 s WAV file to Sarvam and return the English transcript."""
    if not SARVAM_API_KEY:
        raise RuntimeError(
            "SARVAM_API_KEY is not set. Add it to your .env file or environment."
        )

    headers = {"api-subscription-key": SARVAM_API_KEY}
    with open(piece_path, "rb") as fh:
        files = {"file": (os.path.basename(piece_path), fh, "audio/wav")}
        data = {"model": SARVAM_STT_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_URL, headers=headers, files=files, data=data, timeout=120
        )

    response.raise_for_status()
    return response.json().get("transcript", "")


def _transcribe_with_sarvam(chunk_path: str) -> str:
    """
    Transcribe a chunk via Sarvam AI.

    Sarvam's sync API only accepts ≤ 30 s clips, so we slice the chunk
    into SARVAM_PIECE_SECONDS pieces, send each one, then rejoin the results.
    Temporary piece files are always cleaned up regardless of errors.
    """
    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1_000
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    piece_paths: list[str] = []
    texts: list[str] = []

    try:
        for i, start in enumerate(range(0, len(audio), piece_ms)):
            piece = audio[start : start + piece_ms]
            piece_path = f"{chunk_path}_sv_{i}.wav"
            piece.export(piece_path, format="wav")
            piece_paths.append(piece_path)

            logger.debug("Sarvam piece %d/%d: %s", i + 1, total_pieces, piece_path)
            texts.append(_post_piece_to_sarvam(piece_path))
    finally:
        for p in piece_paths:
            if os.path.exists(p):
                os.remove(p)

    return " ".join(texts).strip()


# ── Routing helper ────────────────────────────────────────────────────────────

def _transcribe_chunk(chunk_path: str, language: str) -> str:
    """Route one chunk to Whisper or Sarvam based on the chosen language."""
    if language.lower() == "hinglish":
        return _transcribe_with_sarvam(chunk_path)
    return _transcribe_with_whisper(chunk_path)


# ── Public API ────────────────────────────────────────────────────────────────

def transcribe_all(chunks: list[str], language: str = "english") -> str:
    """
    Transcribe an ordered list of audio chunk paths and return the full text.

    - "english"  → Whisper (sequential; model is not thread-safe on GPU).
    - "hinglish" → Sarvam  (concurrent; I/O-bound API calls).

    Args:
        chunks:   Ordered list of WAV file paths produced by audio_processor.
        language: Transcription backend selector ("english" or "hinglish").

    Returns:
        Full transcript as a single string.
    """
    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    logger.info("Transcribing %d chunk(s) with %s…", len(chunks), engine)

    if language.lower() == "hinglish":
        # Concurrent execution — Sarvam calls are network-bound
        ordered: dict[int, str] = {}

        def _indexed(args: tuple[int, str]) -> tuple[int, str]:
            idx, path = args
            logger.debug("Chunk %d/%d → Sarvam", idx + 1, len(chunks))
            return idx, _transcribe_chunk(path, language)

        with ThreadPoolExecutor(max_workers=SARVAM_MAX_WORKERS) as pool:
            futures = {pool.submit(_indexed, item): item[0] for item in enumerate(chunks)}
            for future in as_completed(futures):
                idx, text = future.result()
                ordered[idx] = text

        full_transcript = " ".join(ordered[i] for i in sorted(ordered))
    else:
        # Sequential — Whisper model is not thread-safe
        texts: list[str] = []
        for i, chunk in enumerate(chunks):
            logger.debug("Chunk %d/%d → Whisper", i + 1, len(chunks))
            texts.append(_transcribe_chunk(chunk, language))
        full_transcript = " ".join(texts)

    logger.info("Transcription complete (%d chars).", len(full_transcript))
    return full_transcript.strip()
