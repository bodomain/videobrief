FROM python:3.12-slim

# System-Dependencies: ffmpeg für Video/Audio-Verarbeitung, nodejs für yt-dlp (--js-runtimes)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg nodejs npm && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python-Dependencies (yt-dlp kommt via pip, aktueller als apt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code
COPY backend/ ./backend/

# Daten-Verzeichnis
RUN mkdir -p /app/data/jobs

# Port
EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
