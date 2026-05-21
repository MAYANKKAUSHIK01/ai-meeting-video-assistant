"""
main.py — CLI entry point for LENS Meeting Intelligence.

Usage:
    python main.py
"""

from __future__ import annotations

import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from core.rag_engine import ask_question
from pipeline import run_pipeline

logging.basicConfig(
    level=logging.WARNING,  # Suppress verbose library output in CLI mode
    format="%(levelname)s | %(name)s | %(message)s",
)

_DIVIDER = "=" * 60


def _section(title: str, content: str) -> None:
    print(f"\n{_DIVIDER}")
    print(f"  {title}")
    print(_DIVIDER)
    print(content)


def main() -> None:
    print("\n🔵 LENS — Meeting Intelligence\n")

    source = input("Enter YouTube URL or local file path: ").strip()
    if not source:
        print("Error: source cannot be empty.")
        sys.exit(1)

    language = input("Language (english / hinglish) [english]: ").strip().lower() or "english"

    model_size = "base"
    if language == "english":
        model_size = input("Whisper Model Size (tiny / base / small / medium) [base]: ").strip().lower() or "base"

    print("\nRunning pipeline… this may take a few minutes.\n")
    result = run_pipeline(source, language, model_size=model_size)

    _section("📌 TITLE", result["title"])
    _section("📋 SUMMARY", result["summary"])
    _section("✅ ACTION ITEMS", result["action_items"])
    _section("🔑 KEY DECISIONS", result["key_decisions"])
    _section("❓ OPEN QUESTIONS", result["open_questions"])

    print(f"\n{_DIVIDER}")
    print("  💬 Chat with your meeting  (type 'exit' to quit)")
    print(_DIVIDER)

    rag_chain = result["rag_chain"]
    while True:
        try:
            question = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            break
        answer = ask_question(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}")

    print("\n👋 Goodbye!\n")


if __name__ == "__main__":
    main()