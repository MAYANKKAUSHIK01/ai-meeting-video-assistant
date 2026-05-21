"""
core/transcriber.py — Speech-to-text transcription engine.

Backends:
  - faster-whisper (local, CPU/GPU) — used for "english"
    * 4-8x faster than openai-whisper on CPU via CTranslate2 INT8 quantization
    * VAD filter skips silent segments automatically
    * Language forced to "en" to skip detection overhead
  - Sarvam AI (cloud API) — used for "hinglish" (translates → English)

Performance improvements:
  - Parallel Sarvam uploads: slices are uploaded concurrently via ThreadPoolExecutor.
  - Multi-model caching: Whisper models are cached by size to avoid reload overhead.
  - VAD and greedy decoding (beam_size=1) for speed.
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
    WHISPER_COMPUTE_TYPE,
    MODELS_DIR,
)

logger = logging.getLogger(__name__)

# ── Cache for multiple Whisper model sizes ────────────────────────────────────
_whisper_models: dict[str, any] = {}


def _load_whisper_model(model_size: str) -> any:
    """
    Load (or return cached) faster-whisper model for the requested size.

    Uses INT8 quantization on CPU for 2-4x extra speedup.
    Uses float16 on CUDA for maximum GPU throughput.
    """
    global _whisper_models
    if model_size not in _whisper_models:
        from faster_whisper import WhisperModel
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        # INT8 on CPU = 2-4x faster, negligible quality loss for speech
        # float16 on GPU = maximum throughput
        compute_type = "float16" if device == "cuda" else WHISPER_COMPUTE_TYPE

        logger.info(
            "Loading faster-whisper model '%s' on '%s' (compute=%s)…",
            model_size, device, compute_type,
        )
        # Use auto cpu threads or system cores to maximise CPU usage
        _whisper_models[model_size] = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            cpu_threads=0, # Auto-select optimum thread count
            download_root=os.path.join(MODELS_DIR, "whisper"),
        )
        logger.info("faster-whisper model '%s' ready.", model_size)
    return _whisper_models[model_size]


# ── faster-whisper backend ────────────────────────────────────────────────────

def _transcribe_with_whisper(chunk_path: str, model_size: str) -> str:
    """
    Transcribe a single WAV chunk with faster-whisper.

    Optimisations:
    - beam_size=1       : greedy decoding — fastest, minimal quality loss
    - language="en"     : skip language-detection pass (~10% overhead saved)
    - vad_filter=True   : CTranslate2 VAD silently skips non-speech segments
    - condition_on_prev : disabled — avoids cross-chunk hallucination
    """
    model = _load_whisper_model(model_size)

    segments, _info = model.transcribe(
        chunk_path,
        language="en",
        beam_size=1,
        best_of=1,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
        compression_ratio_threshold=2.4,
        word_timestamps=False,   # skip word-level alignment = faster
    )

    # Consume generator
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip()


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
    Transcribe via Sarvam AI (hinglish → English).
    Slices chunk into SARVAM_PIECE_SECONDS pieces and uploads them CONCURRENTLY
    to the cloud for maximum performance. Cleans up temp pieces in finally.
    """
    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1_000

    piece_paths: list[str] = []
    try:
        # Create and export all pieces first
        for i, start in enumerate(range(0, len(audio), piece_ms)):
            piece = audio[start : start + piece_ms]
            piece_path = f"{chunk_path}_sv_{i}.wav"
            piece.export(piece_path, format="wav")
            piece_paths.append(piece_path)

        # Upload and transcribe pieces in parallel
        ordered_results: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=SARVAM_MAX_WORKERS) as executor:
            futures = {
                executor.submit(_post_piece_to_sarvam, path): idx
                for idx, path in enumerate(piece_paths)
            }
            for future in as_completed(futures):
                idx = futures[future]
                ordered_results[idx] = future.result()

        # Join in correct order
        transcript = " ".join(ordered_results[i] for i in sorted(ordered_results))
        return transcript.strip()

    finally:
        for p in piece_paths:
            if os.path.exists(p):
                os.remove(p)


# ── Routing helper ────────────────────────────────────────────────────────────

def _transcribe_chunk(chunk_path: str, language: str, model_size: str) -> str:
    if language.lower() == "hinglish":
        return _transcribe_with_sarvam(chunk_path)
    return _transcribe_with_whisper(chunk_path, model_size)


# ── Public API ────────────────────────────────────────────────────────────────

def transcribe_all(
    chunks: list[str],
    language: str = "english",
    model_size: str = "base",
    on_progress: callable | None = None,
) -> str:
    """
    Transcribe an ordered list of WAV chunk paths and return the full text.

    Args:
        chunks:      Ordered list of WAV paths from audio_processor.
        language:    "english" (faster-whisper) or "hinglish" (Sarvam AI).
        model_size:  "tiny" | "base" | "small" | "medium" | "large" (for english mode).
        on_progress: Optional callback invoked as on_progress(done, total)
                     after each chunk completes.

    Returns:
        Full transcript as a single whitespace-joined string.
    """
    engine = "Sarvam AI" if language.lower() == "hinglish" else f"faster-whisper ({model_size})"
    total = len(chunks)
    logger.info("Transcribing %d chunk(s) with %s…", total, engine)

    if language.lower() == "hinglish":
        # Sarvam chunks: network-bound -> run concurrently
        ordered: dict[int, str] = {}

        def _indexed(args: tuple[int, str]) -> tuple[int, str]:
            idx, path = args
            result = _transcribe_chunk(path, language, model_size)
            # Update progress safely
            completed = len(ordered) + 1
            if on_progress:
                on_progress(completed, total)
            return idx, result

        with ThreadPoolExecutor(max_workers=SARVAM_MAX_WORKERS) as pool:
            futures = {pool.submit(_indexed, item): item[0] for item in enumerate(chunks)}
            for future in as_completed(futures):
                idx, text = future.result()
                ordered[idx] = text

        full_transcript = " ".join(ordered[i] for i in sorted(ordered))
    else:
        # Local whisper: CPU/GPU-bound -> sequential (to avoid core thrashing/OOM)
        texts: list[str] = []
        for i, chunk in enumerate(chunks):
            logger.info("Chunk %d/%d -> %s", i + 1, total, engine)
            texts.append(_transcribe_chunk(chunk, language, model_size))
            if on_progress:
                on_progress(i + 1, total)
        full_transcript = " ".join(texts)

    logger.info("Transcription complete (%d chars).", len(full_transcript))
    return full_transcript.strip()
