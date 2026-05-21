"""
config.py — Centralised application configuration.

All environment-variable reads and runtime constants live here.
Import from this module everywhere; never call os.getenv() in core logic files.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ── API Keys ──────────────────────────────────────────────────────────────────
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")

# ── Model selection ───────────────────────────────────────────────────────────
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
# INT8 quantization on CPU gives 2-4x speedup with minimal quality loss.
# On CUDA, float16 is used automatically.
WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
SARVAM_STT_MODEL: str = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")
MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

# ── LLM temperatures ─────────────────────────────────────────────────────────
LLM_TEMP_SUMMARY: float = float(os.getenv("LLM_TEMP_SUMMARY", "0.3"))
LLM_TEMP_EXTRACT: float = float(os.getenv("LLM_TEMP_EXTRACT", "0.2"))
LLM_TEMP_RAG: float = float(os.getenv("LLM_TEMP_RAG", "0.3"))

# ── Audio processing ──────────────────────────────────────────────────────────
# 10-minute chunks: faster per-chunk transcription + better progress granularity.
# Reduce further (e.g. 5) for very fast machines; increase for fewer API calls.
AUDIO_CHUNK_MINUTES: int = int(os.getenv("AUDIO_CHUNK_MINUTES", "10"))
SARVAM_PIECE_SECONDS: int = int(os.getenv("SARVAM_PIECE_SECONDS", "25"))
SARVAM_STT_URL: str = "https://api.sarvam.ai/speech-to-text-translate"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR: str = os.path.join(BASE_DIR, "downloads")
FFMPEG_BIN_DIR: str = os.path.join(BASE_DIR, "ffmpeg_bin")
VECTOR_DB_DIR: str = os.path.join(BASE_DIR, "vector_db")
MODELS_DIR: str = os.path.join(BASE_DIR, "models")

# ── Vector store ──────────────────────────────────────────────────────────────
CHROMA_COLLECTION: str = "meeting_transcript"
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))

# ── Text splitting ────────────────────────────────────────────────────────────
SUMMARY_CHUNK_SIZE: int = 3000
SUMMARY_CHUNK_OVERLAP: int = 200
RAG_CHUNK_SIZE: int = 500
RAG_CHUNK_OVERLAP: int = 50

# ── Sarvam concurrency ────────────────────────────────────────────────────────
SARVAM_MAX_WORKERS: int = int(os.getenv("SARVAM_MAX_WORKERS", "4"))
