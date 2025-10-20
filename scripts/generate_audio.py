# scripts/generate_audio.py
from pathlib import Path
import sys

# Offline TTS + conversion
import pyttsx3
from pydub import AudioSegment
from pydub.utils import which
from sqlalchemy.orm import Session

# Ensure pydub finds ffmpeg.exe
AudioSegment.converter = which("C:\\Users\\SIRI\\ffmpeg\\bin\\ffmpeg.exe")

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from backend.app.db import SessionLocal
from backend.app import crud, models

AUDIO_DIR = ROOT / "backend" / "app" / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def slugify(text: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in (" ", "_", "-") else "_" for ch in text)
    return "_".join(safe.strip().split())[:60] or "name"

def synthesize_mp3_offline(text: str, out_mp3: Path):
    tmp_wav = out_mp3.with_suffix(".wav")
    engine = pyttsx3.init()
    # engine.setProperty("rate", 180)  # optional tweak
    engine.save_to_file(text, str(tmp_wav))
    engine.runAndWait()

    AudioSegment.from_wav(tmp_wav).export(out_mp3, format="mp3")
    try:
        tmp_wav.unlink()
    except FileNotFoundError:
        pass

def generate_missing_audio(limit: int = 500):
    db: Session = SessionLocal()
    try:
        items = (
            db.query(models.Name)
              .filter(models.Name.audio_path == None)  # noqa: E711
              .order_by(models.Name.id)
              .limit(limit)
              .all()
        )
        if not items:
            print("No names pending.")
            return

        for n in items:
            mp3_path = AUDIO_DIR / f"{n.id}_{slugify(n.name)}.mp3"
            try:
                synthesize_mp3_offline(n.name, mp3_path)
                crud.set_audio_path(db, n.id, str(mp3_path))
                print(f"✓ (offline) {n.name} -> {mp3_path}")
            except Exception as e:
                print(f"✗ Failed for {n.name} (id={n.id}): {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_missing_audio()
