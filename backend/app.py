"""VideoBrief FastAPI-Server mit HTMX-Frontend."""

import uuid
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import DATA_DIR, FRAMES_INTERVAL_SEC
from backend.downloader import (
    fetch_metadata,
    download_subtitles,
    download_audio,
    download_video,
    get_job_dir,
)
from backend.transcriber import get_transcript
from backend.frame_extractor import extract_frames
from backend.visual_filter import filter_similar_frames
from backend.llm_analyzer import analyze_video
from backend.report_writer import write_report


# --- Job-Store (einfaches In-Memory-Dict, später SQLite) ---
jobs: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/Shutdown."""
    yield


app = FastAPI(title="VideoBrief", lifespan=lifespan)

# Statische Dateien + Templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# Daten-Verzeichnis für Bilder etc.
app.mount("/data", StaticFiles(directory=str(DATA_DIR.parent)), name="data")


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Startseite mit Eingabeformular."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": jobs,
    })


@app.post("/jobs")
async def create_job(url: str = Form(...)):
    """Neuen Job anlegen und Pipeline starten."""
    try:
        meta = fetch_metadata(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video nicht gefunden: {e}")

    video_id = meta.get("id", str(uuid.uuid4())[:8])
    video_title = meta.get("title", "Unbekannt")

    job_dir = get_job_dir(video_id)

    # Job-Status anlegen
    jobs[video_id] = {
        "id": video_id,
        "url": url,
        "title": video_title,
        "status": "running",
        "step": "Download…",
        "job_dir": str(job_dir),
    }

    # Pipeline im Hintergrund starten
    asyncio.create_task(run_pipeline(video_id, url, video_title, job_dir))

    return RedirectResponse(url=f"/jobs/{video_id}", status_code=303)


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
async def get_job(request: Request, job_id: str):
    """Job-Detailseite."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")

    # Report laden falls fertig
    report = None
    report_path = Path(job["job_dir"]) / "report.md"
    if report_path.exists() and job["status"] == "done":
        report = report_path.read_text(encoding="utf-8")

    return templates.TemplateResponse("job.html", {
        "request": request,
        "job": job,
        "report": report,
    })


@app.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """HTMX-Partial: Job-Status für Polling."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")

    return templates.TemplateResponse("_status.html", {
        "request": None,
        "job": job,
    })


# --- Pipeline ---

async def run_pipeline(video_id: str, url: str, title: str, job_dir: Path):
    """Vollständige Pipeline im Hintergrund ausführen."""
    try:
        # Step 1: Download
        jobs[video_id]["step"] = "Untertitel herunterladen…"
        sub_path = download_subtitles(url, job_dir)

        jobs[video_id]["step"] = "Audio herunterladen…"
        audio_path = download_audio(url, job_dir)

        jobs[video_id]["step"] = "Video herunterladen…"
        video_path = download_video(url, job_dir)

        # Step 2: Transkription
        jobs[video_id]["step"] = "Transkription…"
        transcript = get_transcript(sub_path, audio_path)

        # Transkript speichern
        (job_dir / "transcript.txt").write_text(transcript, encoding="utf-8")

        # Step 3: Frame-Extraktion
        jobs[video_id]["step"] = "Frames extrahieren…"
        all_frames = extract_frames(video_path, job_dir, FRAMES_INTERVAL_SEC)

        # Step 4: Visuelles Filtering
        jobs[video_id]["step"] = "Ähnliche Frames filtern…"
        unique_frames = filter_similar_frames(all_frames)

        # Step 5: LLM-Analyse
        jobs[video_id]["step"] = "Video analysieren (LLM)…"
        analysis = analyze_video(transcript, unique_frames, title)

        # Step 6: Report schreiben
        jobs[video_id]["step"] = "Report generieren…"
        write_report(job_dir, title, url, transcript, analysis, unique_frames)

        # Fertig
        jobs[video_id]["status"] = "done"
        jobs[video_id]["step"] = "Fertig!"

    except Exception as e:
        jobs[video_id]["status"] = "error"
        jobs[video_id]["step"] = f"Fehler: {e}"
        # Fehler ins Log
        error_path = job_dir / "error.txt"
        error_path.write_text(str(e), encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)
