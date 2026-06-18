# VideoBrief

**YouTube Video → Text + Charts + Excalidraw-Präsentation**

Aus Fachvideos, Webinaren und Research-Präsentationen automatisch strukturierte
Notizen inklusive Charts, Kernaussagen und Handlungspunkten erzeugen — plus
eine Excalidraw-Präsentation im Karpathy-Stil (eine große Canvas, alles räumlich verbunden).

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
# macOS: brew install yt-dlp ffmpeg node
# Ubuntu: sudo apt install yt-dlp ffmpeg nodejs

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
Audio/Video herunterladen        (yt-dlp + nodejs JS-Runtime)
   ↓
Transkript erzeugen              (YouTube-Untertitel / Whisper)
   ↓
Frames/Screenshots extrahieren   (ffmpeg, 1 Frame / 2s)
   ↓
Ähnliche Frames entfernen        (imagehash)
   ↓
LLM analysiert Text + Bilder     (OpenAI gpt-4o Vision)
   ↓
Markdown-Report                  (report.md)
   ↓
Excalidraw-Präsentation          (praesentation.excalidraw)
```

## Output pro Job

```text
data/jobs/<video_id>/
  ├── video.mp4
  ├── audio.mp3
  ├── transcript.txt
  ├── frames/
  │   ├── frame_0001.jpg
  │   └── ...
  ├── presentation/
  │   └── praesentation.excalidraw   ← Karpathy-Style Canvas
  ├── report.md
  └── title.md
```

## API

| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| `GET` | `/` | Startseite mit Eingabeformular |
| `POST` | `/jobs` | Neuen Job anlegen (`url=...`) |
| `GET` | `/jobs/{id}` | Job-Detailseite mit Report |
| `GET` | `/jobs/{id}/status` | HTMX-Partial: Live-Status |
| `POST` | `/jobs/{id}/presentation` | Excalidraw-Präsentation generieren |

## Tech-Stack

- **Backend:** Python, FastAPI
- **Frontend:** Jinja2 + HTMX + Tailwind CSS
- **Download:** yt-dlp (mit Node.js JS-Runtime)
- **Video:** ffmpeg
- **Transkription:** YouTube-Untertitel + OpenAI Whisper API
- **Vision:** OpenAI gpt-4o
- **Filter:** imagehash (perceptual hashing)
- **Präsentation:** Excalidraw JSON (Karpathy-Style Canvas)
