"""Transkription: YouTube-Untertitel nutzen oder Whisper-Fallback."""

import re
from pathlib import Path

from openai import OpenAI

from backend.config import OPENAI_API_KEY, OPENAI_TRANSCRIBE_MODEL


def parse_vtt(vtt_path: Path) -> str:
    """VTT-Untertitel in reinen Text umwandeln (Deduplikation)."""
    lines = vtt_path.read_text(encoding="utf-8").splitlines()
    seen = set()
    text_parts = []

    for line in lines:
        line = line.strip()
        # Zeitstempel und WEBVTT-Header überspringen
        if not line or line.startswith("WEBVTT") or "-->" in line or line.isdigit():
            continue
        # HTML-Tags entfernen
        line = re.sub(r"<[^>]+>", "", line)
        if line and line not in seen:
            seen.add(line)
            text_parts.append(line)

    return "\n".join(text_parts)


def transcribe_with_whisper(audio_path: Path) -> str:
    """Audio mit OpenAI Whisper transkribieren."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=OPENAI_TRANSCRIBE_MODEL,
            file=f,
            language="de",
        )
    return transcript.text


def get_transcript(
    subtitle_path: Path | None,
    audio_path: Path,
) -> str:
    """
    Transkript holen: erst Untertitel versuchen, sonst Whisper.
    Gibt (text, quelle) zurück.
    """
    if subtitle_path and subtitle_path.exists():
        text = parse_vtt(subtitle_path)
        if len(text.strip()) > 50:
            return text

    # Fallback: Whisper
    return transcribe_with_whisper(audio_path)
