# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

# Offline TTS + conversion (WAV -> MP3)
import pyttsx3
from pydub import AudioSegment
from pydub.utils import which

# Ensure pydub finds ffmpeg.exe
AudioSegment.converter = which("C:\\Users\\SIRI\\ffmpeg\\bin\\ffmpeg.exe")  # e.g., C:\ffmpeg\bin\ffmpeg.exe via PATH

from .db import Base, engine, get_db
from . import models, schemas, crud

# ---- DB tables ----
Base.metadata.create_all(bind=engine)

# ---- App + CORS ----
app = FastAPI(title="Name Pronunciation Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- TTS / audio helpers ----
AUDIO_DIR = Path("backend/app/static/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def _slugify(text: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in (" ", "_", "-") else "_" for ch in text)
    return "_".join(safe.strip().split())[:60] or "name"

def _synthesize_mp3_offline(text: str, out_mp3: Path):
    """
    Offline synth: pyttsx3 -> WAV, then convert WAV -> MP3 with pydub/FFmpeg.
    """
    tmp_wav = out_mp3.with_suffix(".wav")

    engine = pyttsx3.init()             # Windows SAPI (offline)
    # Optional voice/rate tweaks:
    # engine.setProperty("rate", 180)
    # for v in engine.getProperty("voices"): print(v.id)
    # engine.setProperty("voice", "<voice-id>")
    engine.save_to_file(text, str(tmp_wav))
    engine.runAndWait()

    # Convert to MP3
    AudioSegment.from_wav(tmp_wav).export(out_mp3, format="mp3")
    try:
        tmp_wav.unlink()
    except FileNotFoundError:
        pass

def _generate_audio_task(name_id: int, name: str):
    """Run in background: create MP3 and update audio_path."""
    from .db import SessionLocal
    db = SessionLocal()
    try:
        file_name = f"{name_id}_{_slugify(name)}.mp3"
        path = AUDIO_DIR / file_name
        _synthesize_mp3_offline(name, path)
        crud.set_audio_path(db, name_id, str(path))
        print(f"✓ (offline) Generated: {name} -> {path}")
    except Exception as e:
        print(f"✗ Failed for {name} (id={name_id}): {e}")
    finally:
        db.close()

# ---- API routes ----
@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/names", response_model=list[schemas.NameOut])
def list_names(limit: int = 500, offset: int = 0, db: Session = Depends(get_db)):
    return crud.list_names(db, limit=limit, offset=offset)

@app.get("/api/names/search", response_model=list[schemas.NameOut])
def search_names(q: str, db: Session = Depends(get_db)):
    return crud.search_names(db, q=q)

@app.post("/api/names", response_model=schemas.NameOut, status_code=201)
def create_name(
    payload: schemas.NameCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    n = crud.create_name(db, name)
    # Kick off offline MP3 generation in background
    background_tasks.add_task(_generate_audio_task, n.id, n.name)
    return n

@app.put("/api/names/{name_id}", response_model=schemas.NameOut)
def update_name(
    name_id: int,
    payload: schemas.NameUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    updated = crud.update_name(db, name_id, payload.name)
    if not updated:
        raise HTTPException(status_code=404, detail="Name not found")
    # Regenerate after rename
    background_tasks.add_task(_generate_audio_task, updated.id, updated.name)
    return updated

@app.delete("/api/names/{name_id}", status_code=204)
def delete_name(name_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_name(db, name_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Name not found")

@app.get("/api/audio/{name_id}")
def get_audio(name_id: int, db: Session = Depends(get_db)):
    n = crud.get_name(db, name_id)
    if not n:
        raise HTTPException(status_code=404, detail="Name not found")
    if not n.audio_path:
        raise HTTPException(status_code=404, detail="Audio not generated yet")
    p = Path(n.audio_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Audio file missing")
    # We save MP3, so serve as audio/mpeg
    return FileResponse(p, media_type="audio/mpeg", filename=p.name)

# ---- Static mounts (keep LAST so API routes aren’t shadowed) ----
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
