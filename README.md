## The_name_pronunciation_service-offline-
Offline name pronunciation service - A FastAPI +SQLite web app that lets users add, edit. and play name pronunciations. Uses pyttsx3 + FFmpeg to generate MP3 audio fully offline, with background tasks and an independent batch script. Built with HTML, JS, and Python.


# Setup the environment & install dependencies
Windows (Command Prompt / PowerShell)

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

FFmpeg (required for MP3): (https://ffmpeg.org/download.html)
1. Download ZIP: ffmpeg-release-essentials.zip (gyan.dev)
2. Unzip to: C:\ffmpeg\ → ensure C:\ffmpeg\bin\ffmpeg.exe exists
3. Add C:\ffmpeg\bin to your PATH, open a new terminal, verify in Command Prompt / PowerShell:
   
   ffmpeg -version

Make sure pydub knows your ffmpeg path (already in code):
In backend/app/main.py and scripts/generate_audio.py:
from pydub import AudioSegment
AudioSegment.converter = r"C:\Users\SIRI\ffmpeg\bin\ffmpeg.exe"  # adjust to your path


# Initialize the database
Creates tables and seeds sample names (idempotent).
python -m backend.app.seed


# Run the offline audio generation script (independent process)
Generates MP3 for any names where audio_path is NULL.

python scripts\generate_audio.py

You should see logs like:

✓ (offline) Aarav -> backend/app/static/audio/1_Aarav.mp3


# Start the FastAPI web server

uvicorn backend.app.main:app --reload

App: http://127.0.0.1:8000/
API docs: http://127.0.0.1:8000/docs

Notes:
Adding/updating a name auto-triggers background offline MP3 generation.
Give it ~1–3 seconds after Add/Update before Play works (or reload list).
