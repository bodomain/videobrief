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
- ~~Persistenz: SQLite für MVP?~~ → **In-Memory-Dict** (Disk-Fallback nach Neustart)
- ~~Frontend?~~ → **FastAPI + Jinja2 + HTMX + Tailwind** entschieden
- ~~Frontend-Timing?~~ → direkt im MVP

---

## Status: 2026-06-18

### MVP funktioniert end-to-end ✅

**Getestet mit:**
- `dQw4w9WgXcQ` — Rick Astley (Musikvideo, 80 Frames)
- `x2SdidroweI` — Claude Code Geld verdienen (Tutorial, 31 Frames nach Filter)
- `kqtD5dpn9C8` — Python for Beginners (1h Tutorial, 80 Frames, 12 Timeline-Punkte)

**Pipeline:** URL → Download → Transkript → Frames → Filter → LLM → Report → Excalidraw ✅

**Behobene Issues:**
- yt-dlp braucht Node.js JS-Runtime → Dockerfile + `--js-runtimes nodejs`
- yt-dlp Version zu alt → `>=2025.4.30`
- HTMX `request`-Bug in `_status.html` → `request` durchgereicht
- HTMX Endlos-Polling bei `done` → `outerHTML` + `HX-Redirect`-Endpoint
- HTMX Polling bei 404 (nach Neustart) → globaler `htmx:beforeRequest` Handler
- Jobs nach Container-Neustart weg → `_restore_job_from_disk()` Fallback
- Excalidraw: einzelne Slides → **eine große Canvas** (Karpathy-Stil)
- Report-Parser: nur `###` Format → unterstützt jetzt auch `**Bold:**` Format

---

## Nächste Schritte: LLM-gesteuerte Excalidraw-Präsentation

### Idee

Die aktuelle Excalidraw-Generierung ist template-basiert (deterministisch, immer gleiches Layout).
Stattdessen soll ein **schlaues LLM** aus den strukturierten Daten eine **kreative Präsentation** bauen.

### Architektur: Zwei-Stufen-Ansatz

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  DUMME PIPELINE     │     │  SCHLAUES LLM    │     │  DSL → EXCALIDRAW│
│                     │     │                  │     │                  │
│  • yt-dlp           │     │  Versteht Inhalt │     │  Deterministisch │
│  • ffmpeg           │────▶│  Entscheidet     │────▶│  Baut valides    │
│  • imagehash        │     │  Layout + Story  │     │  Excalidraw-JSON │
│  • Whisper/gpt-4o   │     │                  │     │                  │
│                     │     │  Output: DSL     │     │                  │
└─────────────────────┘     └──────────────────┘     └──────────────────┘
        billig, schnell              kreativ, teuer                robust
```

### Stufe 1: DSL definieren

Einfache Beschreibungssprache für Präsentations-Layouts:

```yaml
canvas:
  width: 4800
  height: 3200
  background: "#ffffff"

sections:
  - id: title
    type: title
    text: "4 Wege mit Claude Code Geld zu verdienen"
    position: [200, 100]
    style: { font_size: 56, color: "#1e1e1e" }

  - id: timeline
    type: flowchart
    direction: horizontal
    nodes:
      - text: "Prozesse automatisieren"
        icon: gear
      - text: "Anwendungen bauen"
        icon: code
      - text: "Beraten"
        icon: people
      - text: "Produkte verkaufen"
        icon: cart
    connections: [0→1, 1→2, 2→3]
    position: [200, 400]

  - id: charts
    type: grid
    columns: 2
    items:
      - frame: frame_0013.jpg
        caption: "Automatisierter E-Mail-Prozess"
      - frame: frame_0146.jpg
        caption: "8-Schritte Geschäftsoptimierung"
    position: [200, 900]
```

### Stufe 2: LLM-Prompt

Das LLM bekommt:
- Den kompletten `report.md`
- Frame-Beschreibungen aus dem Report
- Die DSL-Spezifikation als Schema

Und soll die DSL zurückgeben, z.B.:

```
System: Du bist ein Präsentationsdesigner. Erstelle aus den Videodaten
eine Excalidraw-Präsentation im Karpathy-Stil. Antworte NUR mit YAML
im angegebenen Schema.

User: [report.md content + frame descriptions]

Assistant:
canvas:
  width: 5200
  height: 3600
sections:
  - type: title
    text: "..."
    ...
```

### Stufe 3: DSL → Excalidraw-JSON Converter

Deterministischer Python-Converter (`dsl_to_excalidraw.py`):
- Parse YAML/JSON DSL
- Berechne Positionen (Auto-Layout)
- Generiere valide Excalidraw-Elemente
- Output: `.excalidraw` Datei

**Vorteile dieses Ansatzes:**
- LLM muss kein komplexes JSON-Format kennen
- DSL ist validierbar (Schema)
- Converter ist testbar und deterministisch
- Layout-Logik bleibt kontrollierbar
- LLM kann kreativ sein ohne kaputtzugehen

### Offene Fragen
- DSL-Format: YAML vs. JSON vs. eigene Syntax?
- Welches LLM für den DSL-Step? (gpt-4o, Claude, Gemini?)
- Frames direkt als Bilder in Excalidraw einbetten?
- Auto-Layout-Algorithmus (einfach vs. kraftbasiert)?
