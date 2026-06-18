"""Frames aus Video extrahieren mit ffmpeg."""

import subprocess
from pathlib import Path


def extract_frames(
    video_path: Path,
    output_dir: Path,
    interval_sec: int = 2,
) -> list[Path]:
    """
    Extrahiert alle N Sekunden ein Frame aus dem Video.
    Gibt Liste der Frame-Pfade zurück (sortiert).
    """
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    # Alle Frames mit Zeitstempel als Dateiname
    output_pattern = str(frames_dir / "frame_%04d.jpg")

    subprocess.run(
        [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"fps=1/{interval_sec}",
            "-q:v", "2",  # Qualität (2 = hoch)
            output_pattern,
        ],
        capture_output=True,
        check=True,
    )

    frames = sorted(frames_dir.glob("*.jpg"))
    return frames
