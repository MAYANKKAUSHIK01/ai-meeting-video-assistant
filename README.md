# 🔵 LENS — Meeting Intelligence

> **Transform any meeting recording into structured intelligence — transcription, summarisation, action-item extraction, and live Q&A chat — all in one pipeline.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-green)](https://python.langchain.com)
[![Mistral AI](https://img.shields.io/badge/LLM-Mistral-orange)](https://mistral.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## ✨ Features

| Capability | Detail |
|---|---|
| 🎙️ **Transcription** | Local Whisper (English) or Sarvam AI (Hinglish → English) |
| 📋 **Summarisation** | Map-reduce pipeline — handles arbitrarily long meetings |
| ✅ **Action Items** | Extracts tasks, owners, and deadlines |
| 🔑 **Key Decisions** | Surfaces every agreed outcome |
| ❓ **Open Questions** | Flags unresolved topics for follow-up |
| 💬 **RAG Chat** | Interrogate your meeting with grounded LLM answers |
| 🌐 **Any Source** | YouTube URL or local MP4/MP3/WAV file |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Streamlit UI (app.py)                 │
└───────────────────────────┬─────────────────────────────────┘
                            │ on_step callback
┌───────────────────────────▼─────────────────────────────────┐
│                    pipeline.py (orchestrator)               │
└──┬──────────┬──────────┬──────────┬────────────┬────────────┘
   │          │          │          │            │
   ▼          ▼          ▼          ▼            ▼
audio_    transcriber summarizer  extractor   rag_engine
processor  (Whisper /  (map-reduce (parallel   (ChromaDB +
(yt-dlp +  Sarvam AI)  + Mistral)  Mistral)    Mistral)
 pydub)
```

**Key design decisions:**
- `pipeline.py` is UI-agnostic — works from CLI, Streamlit, or tests.
- `config.py` is the single source of truth for all constants and env vars.
- `core/llm.py` provides a single `get_llm()` factory, eliminating duplication.
- Whisper model is a lazy singleton — loaded once, reused per session.
- Embedding model is a lazy singleton — same pattern.
- Extraction (action items, decisions, questions) runs concurrently via `ThreadPoolExecutor`.

---

## 📁 Project Structure

```
lens-meeting-intelligence/
├── app.py                  # Streamlit entry point
├── pipeline.py             # UI-agnostic pipeline orchestrator
├── main.py                 # CLI entry point
├── config.py               # Centralised configuration
│
├── core/
│   ├── llm.py              # Shared LLM factory (Mistral)
│   ├── transcriber.py      # Whisper + Sarvam backends
│   ├── summarizer.py       # Map-reduce summarisation
│   ├── extractor.py        # Action items / decisions / questions
│   ├── rag_engine.py       # RAG chain builder + Q&A
│   └── vector_store.py     # ChromaDB vector store helpers
│
├── utils/
│   └── audio_processor.py  # FFmpeg bootstrap, yt-dlp, pydub chunking
│
├── ui/
│   └── styles.py           # All Streamlit CSS / font injection
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start (Local)

### 1. Clone the repository

```bash
git clone https://github.com/MAYANKKAUSHIK01/ai-meeting-video-assistant.git
cd ai-meeting-video-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **GPU acceleration (optional):** Install a CUDA-enabled PyTorch build from [pytorch.org](https://pytorch.org/get-started/locally/) before the step above for faster Whisper inference.

### 4. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your MISTRAL_API_KEY (and SARVAM_API_KEY for hinglish)
```

### 5. Run the app

```bash
streamlit run app.py

# Or use the Windows helper script:
run.bat
```

---

## ☁️ Streamlit Cloud Deployment

1. Push the repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch `main`, file `app.py`.
4. Open **Advanced settings → Secrets** and add:

```toml
MISTRAL_API_KEY = "your_key_here"
SARVAM_API_KEY  = "your_key_here"   # optional — only for hinglish
WHISPER_MODEL   = "small"
```

5. Click **Deploy**.

> ⚠️ Whisper runs locally; Streamlit Cloud's free tier has limited RAM. Use `WHISPER_MODEL=tiny` or `base` for cloud deployment to avoid OOM errors.

---

## 🖥️ CLI Usage

```bash
python main.py
# Enter YouTube URL or local file path: https://youtube.com/watch?v=...
# Language (english / hinglish) [english]: english
```

---

## 🔑 API Keys

| Key | Where to get it | Required? |
|---|---|---|
| `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai) | ✅ Always |
| `SARVAM_API_KEY` | [sarvam.ai](https://sarvam.ai) | ⚠️ Hinglish only |

---

## 🛠️ Configuration Reference

All settings live in `.env`:

| Variable | Default | Description |
|---|---|---|
| `WHISPER_MODEL` | `base` | `tiny` / `base` / `small` / `medium` / `large` |
| `WHISPER_COMPUTE_TYPE` | `int8` | Quantization for CPU speedup: `int8` / `float16` |
| `MISTRAL_MODEL` | `mistral-small-latest` | Mistral model name |
| `AUDIO_CHUNK_MINUTES` | `10` | Audio chunk length for transcription |
| `RAG_TOP_K` | `4` | Chunks retrieved per RAG query |
| `SARVAM_MAX_WORKERS` | `4` | Concurrent Sarvam API calls |

---

## 📸 Screenshots

<!-- Add screenshots here after deployment -->
| Landing | Analysis Results | Chat |
|---------|-----------------|------|
| *coming soon* | *coming soon* | *coming soon* |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repo
2. Create your feature branch: `git checkout -b feat/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push: `git push origin feat/amazing-feature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
