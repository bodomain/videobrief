"""Markdown-Report generieren aus Analyse-Ergebnissen."""

from pathlib import Path


def write_report(
    job_dir: Path,
    video_title: str,
    video_url: str,
    transcript: str,
    analysis: dict,
    frame_paths: list[Path],
) -> Path:
    """
    Schreibt den Markdown-Report ins Job-Verzeichnis.
    Gibt Pfad zur report.md zurück.
    """
    report_path = job_dir / "report.md"

    # Transkript separat speichern
    transcript_path = job_dir / "transcript.txt"
    transcript_path.write_text(transcript, encoding="utf-8")

    # Titel als separate Datei
    title_path = job_dir / "title.md"
    title_path.write_text(video_title, encoding="utf-8")

    # Report zusammenbauen
    report = []
    report.append(f"# {video_title}\n")
    report.append(f"**Quelle:** [{video_url}]({video_url})\n")
    report.append("")

    # Analyse hinzufügen
    raw_analysis = analysis.get("raw_analysis", "Keine Analyse verfügbar.")
    report.append(raw_analysis)
    report.append("")

    # Referenz auf verwendete Frames
    report.append("---\n")
    report.append("## Verwendete Frames\n")
    report.append(f"Anzahl analysierter Frames: {analysis.get('frames_analyzed', 0)}\n")

    if frame_paths:
        report.append("\nFrame-Dateien:\n")
        for i, frame_path in enumerate(frame_paths, 1):
            report.append(f"- `{frame_path.name}`\n")

    # Transkript-Referenz
    report.append("\n---\n")
    report.append("## Vollständiges Transkript\n")
    report.append(f"Siehe `transcript.txt` ({analysis.get('transcript_length', 0)} Zeichen)\n")

    # Datei schreiben
    report_content = "\n".join(report)
    report_path.write_text(report_content, encoding="utf-8")

    return report_path
