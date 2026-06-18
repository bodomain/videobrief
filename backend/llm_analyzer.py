"""LLM-Analyse: Transkript + Frames → strukturierte Insights."""

import base64
from pathlib import Path

from openai import OpenAI

from backend.config import OPENAI_API_KEY, OPENAI_VISION_MODEL


def encode_image(image_path: Path) -> str:
    """Bild als Base64 encode für OpenAI Vision API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_video(
    transcript: str,
    frame_paths: list[Path],
    video_title: str = "",
) -> dict:
    """
    Analysiert Transkript + Frames mit OpenAI Vision.
    Gibt strukturiertes dict mit Kernaussagen, Charts, etc. zurück.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    # System-Prompt
    system_prompt = """Du bist ein Experte für Videoanalyse. Du erhältst das Transkript
und ausgewählte Frames aus einem Video. Deine Aufgabe:

1. Fasse die Kernaussage zusammen (2-3 Sätze)
2. Erstelle eine Timeline der wichtigsten Punkte
3. Identifiziere und beschreibe Charts/Visualisierungen
4. Fasse den Argumentationsgang zusammen
5. Notiere offene Fragen oder Unsicherheiten

Antworte strukturiert auf Deutsch. Sei präzise und faktentreu.
Wenn du etwas nicht sicher weißt, sage das explizit."""

    # User-Content zusammenbauen
    user_content = []

    # Text-Teil
    text_part = f"Video-Titel: {video_title}\n\nTranskript:\n{transcript}\n\n"
    text_part += f"Anzahl Frames zur Analyse: {len(frame_paths)}\n\n"
    text_part += "Analysiere die Frames im Kontext des Transkripts."
    user_content.append({"type": "text", "text": text_part})

    # Bilder hinzufügen (max 20 für API-Limits)
    for i, frame_path in enumerate(frame_paths[:20]):
        try:
            b64_image = encode_image(frame_path)
            user_content.append({
                "type": "text",
                "text": f"Frame {i+1} (bei {frame_path.stem}):",
            })
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_image}",
                    "detail": "low",  # Kosten sparen
                },
            })
        except Exception as e:
            # Fehlerhafte Frames überspringen
            continue

    # API-Call
    response = client.chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=4000,
        temperature=0.3,
    )

    analysis_text = response.choices[0].message.content

    # Strukturierte Ausgabe parsen (einfache Extraktion)
    return {
        "raw_analysis": analysis_text,
        "frames_analyzed": len(frame_paths),
        "transcript_length": len(transcript),
    }
