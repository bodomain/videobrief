"""Ähnliche Frames herausfiltern (Deduplikation)."""

import imagehash
from PIL import Image
from pathlib import Path

from backend.config import MAX_FRAMES_FOR_LLM


def filter_similar_frames(
    frame_paths: list[Path],
    hash_size: int = 8,
    threshold: int = 10,
    max_frames: int = MAX_FRAMES_FOR_LLM,
) -> list[Path]:
    """
    Filtert ähnliche Frames mittels Perceptual Hash.
    Behält nur Frames, die sich ausreichend unterscheiden.
    Begrenzt auf max_frames.
    """
    if not frame_paths:
        return []

    unique_frames = []
    unique_hashes = []

    for frame_path in frame_paths:
        try:
            img = Image.open(frame_path)
            img_hash = imagehash.phash(img, hash_size=hash_size)

            # Prüfen ob ähnlicher Frame schon dabei
            is_unique = True
            for existing_hash in unique_hashes:
                if abs(img_hash - existing_hash) < threshold:
                    is_unique = False
                    break

            if is_unique:
                unique_frames.append(frame_path)
                unique_hashes.append(img_hash)

                if len(unique_frames) >= max_frames:
                    break

        except Exception as e:
            # Fehlerhafte Frames überspringen
            continue

    return unique_frames
