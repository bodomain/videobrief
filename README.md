# VideoBrief

**YouTube Video → Text + Charts**

Aus Fachvideos, Webinaren und Research-Präsentationen automatisch strukturierte
Notizen inklusive Charts, Kernaussagen und Handlungspunkten erzeugen.

## Setup

```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. System-Tools (falls nicht vorhanden)
# macOS: brew install yt-dlp ffmpeg
# Ubuntu: sudo apt install yt-dlp ffmpeg

# 3. OpenAI API Key
cp .env.example .env
# OPENAI_API_KEY in .env eintragen
```

## Starten

```bash
cd /home/user/Desktop/videobrief
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
# videobrief
