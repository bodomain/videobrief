"""Konfiguration und Settings für VideoBrief."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Pfade
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "jobs"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
OPENAI_TRANSCRIBE_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1")

# Frame-Extraktion
FRAMES_INTERVAL_SEC = 2  # 1 Frame alle N Sekunden
MAX_FRAMES_FOR_LLM = 80  # Obergrenze für Vision-LLM

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
