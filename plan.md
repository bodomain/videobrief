# Plan: VideoBrief — YouTube Video → Text + Charts

## Ziel

Aus Fachvideos, Webinaren und Research-Präsentationen automatisch strukturierte
Notizen inklusive Charts, Kernaussagen und Handlungspunkten erzeugen.

**Pitch:**
> Ich extrahiere aus Fachvideos, Webinaren und Research-Präsentationen automatisch
> strukturierte Notizen inklusive Charts, Kernaussagen und Handlungspunkten.

Zielbranchen: Asset Management, Research, Energie, Klima, Data Analytics.

---

## Pipeline (Kernidee)

```text
YouTube-URL
   ↓
Audio/Video herunterladen        (yt-dlp)
   ↓
Transkript erzeugen              (YouTube-Untertitel / Whisper)
   ↓
Frames/Screenshots extrahieren   (ffmpeg + OpenCV)
   ↓
Ähnliche Frames entfernen        (imagehash / scenedetect)
   ↓
LLM analysiert Text + Bilder     (OpenAI / Claude / Gemini)
   ↓
Markdown-Report mit eingebetteten Charts
```

---

## Ausbaustufen

| Version         | Ergebnis                                                            | Aufwand    |
| --------------- | ------------------------------------------------------------------- | ---------- |
| MVP             | URL → Transkript + Screenshots + Markdown-Summary                   | 2–5 Tage   |
| Solide App      | Web-UI, Jobs, Speicherung, Export `.md` / `.pdf`                    | 2–4 Wochen |
| Starkes Produkt | Chart-Erkennung, Folienclustering, PPTX-Export, Nutzerkonten        | 1–3 Monate |

Aktueller Fokus: **MVP**.

---

## Tech-Stack (MVP)

```text
Python
FastAPI + Jinja2 + HTMX (Frontend im MVP)
yt-dlp
ffmpeg
OpenAI API (Whisper Transkription + gpt-4o Vision)
SQLite (später PostgreSQL)
Markdown-Export
später: React/Next.js Frontend (wenn nötig)
```

**Frontend-Entscheidung:** FastAPI + Jinja2-Templates + HTMX + Tailwind.
Serverseitig gerendert, Job-Progress via HTMX (SSE/Partial-Updates),
kein separates JS-Frontend nötig. Migrationspfad zu Next.js bleibt offen.

---

## LLM-APIs

### Transkription
- **MVP (entschieden):** YouTube-Untertitel per `yt-dlp`, falls vorhanden
- **Fallback (entschieden):** OpenAI Audio API (Whisper)
- **Optional später:** Gemini Audio/Video

### Bild-/Chart-Verständnis (Vision)
- **MVP (entschieden):** OpenAI Vision (gpt-4o / gpt-4o-mini) für einzelne Frames
- **Experiment:** Gemini direkt mit Video/YouTube-URL
- **Robust:** eigener Frame-Extractor + Vision-LLM
- **Skalierung/Kosten später:** Qwen2.5-VL / InternVL selbst hosten (stark bei Charts/OCR)

---

## Wichtigster Engineering-Trick

**Nicht jedes Frame ans LLM schicken** — zu teuer und langsam.

```text
Video 30 min
   ↓
1 Frame / 2 s = 900 Bilder
   ↓
Duplikat-/Ähnlichkeitserkennung (imagehash, scenedetect)
   ↓
20–80 relevante Bilder
   ↓
nur diese ans Vision-Modell
```

Tools: `ffmpeg`, `OpenCV`, `imagehash`, `scenedetect`.

---

## MVP-Funktionsumfang

**Input:** YouTube-URL

**Output:**
```text
title.md
transcript.txt
/images/frame_001.jpg
summary.md
```

`summary.md` Struktur:

```markdown
# Video Summary

## Kernaussage

## Timeline

## Wichtige Charts / Visuals

### Chart 1 – <Titel>
![Chart](images/frame_012.jpg)

Interpretation:
...

## Argumentationsgang

## Offene Fragen / Unsicherheiten
```

---

## Architektur

```text
backend/
  app.py                 FastAPI
  downloader.py          yt-dlp wrapper
  transcriber.py         Whisper / subtitles
  frame_extractor.py     ffmpeg + OpenCV
  visual_filter.py       duplicate removal
  llm_analyzer.py        OpenAI/Claude/Gemini
  report_writer.py       Markdown export

data/
  jobs/
    job_id/
      video.mp4
      audio.mp3
      transcript.vtt
      frames/
      report.md
```

---

## Schwierigkeiten (bewusst steuern)

1. Gute Frame-Auswahl
2. Chart-Bedeutung korrekt erklären
3. Halluzinationen vermeiden
4. Lange Videos chunkweise zusammenführen
5. Urheberrecht / YouTube-ToS sauber handhaben

---

## MVP-Aufgabenliste

- [ ] Projektstruktur `backend/` + `data/jobs/` anlegen
- [ ] `downloader.py` — yt-dlp Wrapper (Video + Audio + Untertitel)
- [ ] `transcriber.py` — Untertitel nutzen, sonst Whisper
- [ ] `frame_extractor.py` — ffmpeg, 1 Frame / 2 s
- [ ] `visual_filter.py` — Ähnlichkeitserkennung (imagehash/scenedetect)
- [ ] `llm_analyzer.py` — Vision-LLM-Analyse der ausgewählten Frames + Transkript
- [ ] `report_writer.py` — Markdown-Report generieren
- [ ] `app.py` — FastAPI-Endpunkt `POST /jobs` + `GET /jobs/{id}`
- [ ] Secrets/Keys via `.env` handhaben
- [ ] README mit Startanleitung

---

## Offene Entscheidungen

- ~~Welches Vision-LLM als erstes?~~ → **OpenAI (gpt-4o / gpt-4o-mini)** entschieden
- ~~Whisper lokal vs. OpenAI API?~~ → **OpenAI Audio API (Whisper)** entschieden
- ~~Persistenz: SQLite für MVP?~~ → **SQLite** entschieden
- ~~Frontend?~~ → **FastAPI + Jinja2 + HTMX + Tailwind** entschieden
- ~~Frontend-Timing?~~ → direkt im MVP
