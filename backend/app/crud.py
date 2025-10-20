# backend/app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

def list_names(db: Session, limit: int = 500, offset: int = 0):
    return db.query(models.Name).order_by(models.Name.id).offset(offset).limit(limit).all()

def search_names(db: Session, q: str, limit: int = 200):
    like = f"%{q.lower()}%"
    return (db.query(models.Name)
            .filter(func.lower(models.Name.name).like(like))
            .order_by(models.Name.id)
            .limit(limit)
            .all())

def get_name(db: Session, name_id: int):
    return db.query(models.Name).filter(models.Name.id == name_id).first()

def create_name(db: Session, name: str):
    n = models.Name(name=name.strip(), audio_path=None)
    db.add(n); db.commit(); db.refresh(n)
    return n

def update_name(db: Session, name_id: int, new_name: str):
    n = get_name(db, name_id)
    if not n: return None
    n.name = new_name.strip()
    n.audio_path = None  # force regen
    db.commit(); db.refresh(n)
    return n

def delete_name(db: Session, name_id: int):
    n = get_name(db, name_id)
    if not n: return False
    db.delete(n); db.commit()
    return True

def set_audio_path(db: Session, name_id: int, audio_path: str | None):
    n = get_name(db, name_id)
    if not n: return None
    n.audio_path = audio_path
    db.commit(); db.refresh(n)
    return n
