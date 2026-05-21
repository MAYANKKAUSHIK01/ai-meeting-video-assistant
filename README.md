
<div align="center">
  
# 🔵 LENS — Meeting Intelligence

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="https://github.com/user-attachments/assets/9345997c-3283-4fde-8603-ab0b928dca2b" 
             width="420" height="240" style="object-fit:cover; border-radius:8px;"/>
        <br/><sub><b>🏠 Dashboard Overview</b></sub>
      </td>
      <td align="center">
        <img src="https://github.com/user-attachments/assets/36795106-5342-42ce-9b2e-7ed6a6b12dcf" 
             width="420" height="240" style="object-fit:cover; border-radius:8px;"/>
        <br/><sub><b>📋 Summary & Key Decisions</b></sub>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://github.com/user-attachments/assets/f79c171c-7606-48a4-aad8-7f4c07508fe5" 
             width="420" height="240" style="object-fit:cover; border-radius:8px;"/>
        <br/><sub><b>✅ Action Items Extraction</b></sub>
      </td>
      <td align="center">
        <img src="https://github.com/user-attachments/assets/30feb11c-3ccc-4a5f-83bd-f31e045d67c2"
             width="420" height="240" style="object-fit:cover; border-radius:8px;"/>
        <br/><sub><b>💬 RAG Chat Q&A</b></sub>
      </td>
    </tr>
  </table>
</div>>
### *Transform any meeting recording into structured intelligence*
**Transcription · Summarisation · Action Items · Live Q&A Chat — all in one pipeline**

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-2ECC71?style=for-the-badge)](https://python.langchain.com)
[![Mistral AI](https://img.shields.io/badge/LLM-Mistral_AI-FF7000?style=for-the-badge)](https://mistral.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-F1C40F?style=for-the-badge)](LICENSE)

<br/>

[🚀 Quick Start](#-quick-start-local) &nbsp;·&nbsp; [☁️ Cloud Deploy](#%EF%B8%8F-streamlit-cloud-deployment) &nbsp;·&nbsp; [🏗️ Architecture](#%EF%B8%8F-architecture) &nbsp;·&nbsp; [💻 CLI](#%EF%B8%8F-cli-usage) &nbsp;·&nbsp; [🤝 Contributing](#-contributing)

</div>

---

> **Drop in any meeting recording — YouTube URL or local MP4/MP3/WAV — and LENS returns a full intelligence report: transcript, executive summary, action items with owners & deadlines, key decisions, open questions, and a live RAG chat to interrogate the content.**

---

## ✨ Features

| Capability | Detail |
|---|---|
| 🎙️ **Transcription** | Local Whisper (English) or Sarvam AI (Hinglish → English) |
| 📋 **Summarisation** | Map-reduce pipeline — handles arbitrarily long meetings without truncation |
| ✅ **Action Items** | Extracts tasks, owners, and deadlines automatically |
| 🔑 **Key Decisions** | Surfaces every agreed outcome so nothing slips through the cracks |
| ❓ **Open Questions** | Flags unresolved topics for follow-up |
| 💬 **RAG Chat** | Interrogate your meeting with grounded LLM answers via ChromaDB + Mistral |
| 🌐 **Any Source** | YouTube URL or local MP4 / MP3 / WAV file |
| ⚡ **Parallel Extraction** | Action items, decisions & questions extracted concurrently via `ThreadPoolExecutor` |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Streamlit UI (app.py)                 │
│                  ← on_step callback for live updates →      │
└───────────────────────────┬─────────────────────────────────┘
                            │
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
- `pipeline.py` is **UI-agnostic** — works from CLI, Streamlit, or tests without modification.
- `config.py` is the **single source of truth** for all constants and env vars; no magic strings scattered across the codebase.
- `core/llm.py` provides a single `get_llm()` factory, eliminating LLM instantiation duplication.
- **Whisper model is a lazy singleton** — loaded once on first use, reused per session to avoid cold-start delays.
- **Embedding model is a lazy singleton** — same pattern; prevents redundant downloads between RAG queries.
- **Extraction runs concurrently** via `ThreadPoolExecutor` — action items, decisions, and questions are processed in parallel, cutting post-transcription latency significantly.

---

## 📁 Project Structure

```
lens-meeting-intelligence/
├── app.py                  # 🖥️  Streamlit entry point & UI logic
├── pipeline.py             # ⚙️  UI-agnostic pipeline orchestrator
├── main.py                 # 💻  CLI entry point
├── config.py               # 🔧  Centralised configuration & env vars
│
├── core/
│   ├── llm.py              # 🤖  Shared LLM factory (Mistral)
│   ├── transcriber.py      # 🎙️  Whisper + Sarvam backends
│   ├── summarizer.py       # 📋  Map-reduce summarisation pipeline
│   ├── extractor.py        # ✅  Action items / decisions / open questions
│   ├── rag_engine.py       # 💬  RAG chain builder + Q&A interface
│   └── vector_store.py     # 🗄️  ChromaDB vector store helpers
│
├── utils/
│   └── audio_processor.py  # 🎧  FFmpeg bootstrap, yt-dlp download, pydub chunking
│
├── ui/
│   └── styles.py           # 🎨  All Streamlit CSS / font injection
│
├── requirements.txt        # 📦  Python dependencies
├── .env.example            # 🔑  Environment variable template
├── run.bat                 # 🪟  Windows one-click launcher
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start (Local)

### Prerequisites

Before you begin, make sure you have:
- **Python 3.10+** installed
- **`ffmpeg`** on your PATH — [installation guide](https://ffmpeg.org/download.html)
- A **Mistral API key** — [get one free at console.mistral.ai](https://console.mistral.ai)

---

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

> 💡 **GPU acceleration (optional):** Install a CUDA-enabled PyTorch build from [pytorch.org](https://pytorch.org/get-started/locally/) *before* the step above for significantly faster Whisper inference on long recordings.

### 4. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```dotenv
MISTRAL_API_KEY=sk-...          # Required — always
SARVAM_API_KEY=your_key_here    # Only needed for Hinglish transcription
WHISPER_MODEL=small             # tiny | base | small | medium | large
```

### 5. Run the app

```bash
streamlit run app.py

# Or use the Windows helper script:
run.bat
```

The app opens at **http://localhost:8501** — paste a YouTube URL or upload a local file and click **Analyse**.

---

## ☁️ Streamlit Cloud Deployment

Deploy LENS publicly in under 5 minutes:

1. Push the repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch `main`, file `app.py`.
4. Open **Advanced settings → Secrets** and add:

```toml
MISTRAL_API_KEY = "your_key_here"
SARVAM_API_KEY  = "your_key_here"   # optional — only for Hinglish
WHISPER_MODEL   = "small"
```

5. Click **Deploy**.

> ⚠️ **Memory note:** Whisper runs locally inside the Streamlit Cloud container. The free tier has limited RAM — use `WHISPER_MODEL=tiny` or `base` to avoid OOM errors on long recordings. For production workloads, consider a paid tier or a self-hosted VM.

---

## 🖥️ CLI Usage

Prefer the terminal? LENS ships with a minimal CLI:

```bash
python main.py
# Enter YouTube URL or local file path: https://youtube.com/watch?v=...
# Language (english / hinglish) [english]: english
```

---

## 🔑 API Keys

| Key | Where to get it | Required? |
|---|---|:---:|
| `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai) | ✅ Always |
| `SARVAM_API_KEY` | [sarvam.ai](https://sarvam.ai) | ⚠️ Hinglish only |

---

## 🛠️ Configuration Reference

All settings live in `.env` (or Streamlit Secrets for cloud deployments):

| Variable | Default | Description |
|---|:---:|---|
| `WHISPER_MODEL` | `small` | `tiny` / `base` / `small` / `medium` / `large` |
| `MISTRAL_MODEL` | `mistral-small-latest` | Mistral model name |
| `AUDIO_CHUNK_MINUTES` | `20` | Audio chunk length for transcription batching |
| `RAG_TOP_K` | `4` | Chunks retrieved per RAG query |
| `SARVAM_MAX_WORKERS` | `4` | Concurrent Sarvam API calls for Hinglish chunks |

---

## 🗺️ Roadmap

- [ ] Speaker diarisation (who said what)
- [ ] Multi-language support beyond English / Hinglish
- [ ] Exportable PDF / Notion reports
- [ ] Slack / Teams webhook for auto-posting summaries
- [ ] Scheduled analysis via cron / GitHub Actions

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

---

<div align="center">

Built with ❤️ by [Mayank Kaushik](https://github.com/MAYANKKAUSHIK01)

*If LENS saved you time, consider giving it a ⭐ on GitHub!*

</div>
