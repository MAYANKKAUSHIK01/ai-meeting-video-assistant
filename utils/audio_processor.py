"""
utils/audio_processor.py — Audio acquisition and pre-processing.

Responsibilities:
  - Bootstrap FFmpeg from imageio-ffmpeg bundle (Windows-safe, no system install needed).
  - Download audio from YouTube URLs via yt-dlp.
  - Convert any local audio/video file to a 16 kHz mono WAV.
  - Chunk a WAV file into fixed-length segments for Whisper / Sarvam.
  - Top-level process_input() entry point consumed by the pipeline.
"""

from __future__ import annotations

import logging
import os
import re
import shutil

import imageio_ffmpeg
import yt_dlp
from pydub import AudioSegment

from config import AUDIO_CHUNK_MINUTES, DOWNLOAD_DIR, FFMPEG_BIN_DIR

logger = logging.getLogger(__name__)

# ── FFmpeg bootstrap ──────────────────────────────────────────────────────────
# imageio-ffmpeg ships its own binary (e.g. ffmpeg-win-x86_64-v7.1.exe).
# yt-dlp requires the binary to be named exactly "ffmpeg.exe" inside the
# directory passed to ffmpeg_location, so we copy it once on first run.

_FFMPEG_SRC = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(FFMPEG_BIN_DIR, exist_ok=True)

_FFMPEG_EXE = os.path.join(FFMPEG_BIN_DIR, "ffmpeg.exe")
if not os.path.exists(_FFMPEG_EXE):
    shutil.copy2(_FFMPEG_SRC, _FFMPEG_EXE)
    logger.info("FFmpeg binary copied to %s", _FFMPEG_EXE)

# Tell pydub and PATH where the binary lives
AudioSegment.converter = _FFMPEG_EXE
AudioSegment.ffmpeg = _FFMPEG_EXE
os.environ["PATH"] = FFMPEG_BIN_DIR + os.pathsep + os.environ.get("PATH", "")
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _sanitize_filename(raw: str) -> str:
    """Strip characters that are illegal in Windows/Linux file names."""
    return re.sub(r'[\\/:*?"<>|]', "_", raw)


def download_youtube_audio(url: str) -> str:
    """
    Download audio from a YouTube URL and return the path to the resulting WAV.

    Uses yt-dlp with FFmpegExtractAudio post-processor so the file is
    already in WAV format at download time — no secondary conversion needed.
    """
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "ffmpeg_location": FFMPEG_BIN_DIR,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        # Sanitise the title so the filename is always safe on all OSes
        "restrictfilenames": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # prepare_filename gives the pre-postprocessor name; swap extension
        raw_path = ydl.prepare_filename(info)

    wav_path = os.path.splitext(raw_path)[0] + ".wav"
    if not os.path.exists(wav_path):
        # Fallback: walk DOWNLOAD_DIR for the newest .wav (yt-dlp edge case)
        wavs = sorted(
            (os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".wav")),
            key=os.path.getmtime,
            reverse=True,
        )
        if not wavs:
            raise FileNotFoundError("yt-dlp download completed but no WAV file was found.")
        wav_path = wavs[0]

    logger.info("Downloaded audio: %s", wav_path)
    return wav_path


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio/video file to a 16 kHz mono WAV.

    Returns the path to the converted WAV file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    base = os.path.splitext(input_path)[0]
    output_path = f"{base}_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16_000)
    audio.export(output_path, format="wav")

    logger.info("Converted to WAV: %s", output_path)
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = AUDIO_CHUNK_MINUTES) -> list[str]:
    """
    Split a WAV file into fixed-length chunks and return their file paths.

    Args:
        wav_path:      Absolute path to the source WAV.
        chunk_minutes: Length of each chunk in minutes (default from config).

    Returns:
        Ordered list of chunk file paths.
    """
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1_000

    chunks: list[str] = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    logger.info("Audio chunked into %d segment(s).", len(chunks))
    return chunks


def process_input(source: str) -> list[str]:
    """
    Top-level entry point for the audio pipeline.

    Accepts either:
      - A YouTube / web URL  → downloads and extracts audio.
      - A local file path    → converts to WAV if necessary.

    Returns an ordered list of WAV chunk paths ready for transcription.
    """
    source = source.strip()
    if source.startswith(("http://", "https://")):
        logger.info("Detected URL — downloading audio from: %s", source)
        wav_path = download_youtube_audio(source)
    else:
        logger.info("Detected local file — converting: %s", source)
        wav_path = convert_to_wav(source)

    chunks = chunk_audio(wav_path)
    logger.info("process_input complete: %d chunk(s) ready.", len(chunks))
    return chunks
