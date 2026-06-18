# VideoBrief

**YouTube Video → Text + Charts**

Aus Fachvideos, Webinaren und Research-Präsentationen automatisch strukturierte
Notizen inklusive Charts, Kernaussagen und Handlungspunkten erzeugen.

## Setup

### Mit Docker (empfohlen)

```bash
# 1. OpenAI API Key konfigurieren
cp .env.example .env
nano .env  # OPENAI_API_KEY eintragen

# 2. Container starten
docker compose up -d
# → http://localhost:8000
```

**Logs ansehen:**
```bash
docker compose logs -f
```

**Stoppen:**
```bash
docker compose down
```

### Lokal (für Entwicklung)

```bash
# 1. System-Tools installieren
# macOS: brew install yt-dlp ffmpeg
# Ubuntu: sudo apt install yt-dlp ffmpeg

# 2. Python-Dependencies
pip install -r requirements.txt

# 3. OpenAI API Key
cp .env.example .env
# OPENAI_API_KEY in .env eintragen

# 4. Server starten
python -m uvicorn backend.app:app --reload
# → http://localhost:8000
```

## Pipeline

```text
YouTube-URL
   ↓
Audio/Video herunterladen        (yt-dlp)
   ↓
Transkript erzeugen              (YouTube-Untertitel / Whisper)
   ↓
Frames/Screenshots extrahieren   (ffmpeg, 1 Frame / 2s)
   ↓
Ähnliche Frames entfernen        (imagehash)
   ↓
LLM analysiert Text + Bilder     (OpenAI gpt-4o Vision)
   ↓
Markdown-Report mit Charts
```

## Output pro Job

```text
data/jobs/<video_id>/
  ├── video.mp4
  ├── audio.mp3
  ├── transcript.txt
  ├── frames/
  │   ├── frame_0001.jpg
  │   ├── frame_0002.jpg
  │   └── ...
  ├── report.md
  └── title.md
```

## Tech-Stack

- **Backend:** Python, FastAPI
- **Frontend:** Jinja2 + HTMX + Tailwind CSS
- **Download:** yt-dlp
- **Video:** ffmpeg
- **Transkription:** YouTube-Untertitel + OpenAI Whisper API
- **Vision:** OpenAI gpt-4o
- **Filter:** imagehash (perceptual hashing)
