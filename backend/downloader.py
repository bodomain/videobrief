"""YouTube-Video/Audio/Untertitel herunterladen via yt-dlp."""

import json
import subprocess
from pathlib import Path

from backend.config import DATA_DIR


def get_job_dir(video_id: str) -> Path:
    """Job-Verzeichnis für ein Video anlegen/zurückgeben."""
    job_dir = DATA_DIR / video_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def fetch_metadata(url: str) -> dict:
    """Video-Metadaten holen (ohne Download)."""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-download", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def download_subtitles(url: str, job_dir: Path) -> Path | None:
    """Untertitel herunterladen (Deutsch bevorzugt, dann Englisch)."""
    out_template = str(job_dir / "subs.%(ext)s")

    # Erst deutsch versuchen, dann englisch
    for lang in ["de", "en"]:
        try:
            subprocess.run(
                [
                    "yt-dlp",
                    "--write-sub",
                    "--write-auto-sub",
                    "--sub-lang", lang,
                    "--sub-format", "vtt",
                    "--skip-download",
                    "-o", out_template,
                    url,
                ],
                capture_output=True,
                check=True,
            )
            # Suche die heruntergeladene Datei
            for f in job_dir.glob("subs.*.vtt"):
                return f
        except subprocess.CalledProcessError:
            continue

    return None


def download_audio(url: str, job_dir: Path) -> Path:
    """Audio als MP3 herunterladen."""
    out_template = str(job_dir / "audio.%(ext)s")
    subprocess.run(
        [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", out_template,
            url,
        ],
        capture_output=True,
        check=True,
    )
    audio_files = list(job_dir.glob("audio.*"))
    if not audio_files:
        raise RuntimeError(f"Audio-Download fehlgeschlagen für {url}")
    return audio_files[0]


def download_video(url: str, job_dir: Path) -> Path:
    """Video herunterladen (für Frame-Extraktion)."""
    out_template = str(job_dir / "video.%(ext)s")
    subprocess.run(
        [
            "yt-dlp",
            "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "--merge-output-format", "mp4",
            "-o", out_template,
            url,
        ],
        capture_output=True,
        check=True,
    )
    video_files = list(job_dir.glob("video.*"))
    if not video_files:
        raise RuntimeError(f"Video-Download fehlgeschlagen für {url}")
    return video_files[0]
