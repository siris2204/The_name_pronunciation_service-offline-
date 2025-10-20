# backend/app/schemas.py
from pydantic import BaseModel

class NameBase(BaseModel):
    name: str

class NameCreate(NameBase):
    pass

class NameUpdate(BaseModel):
    name: str

class NameOut(BaseModel):
    id: int
    name: str
    audio_path: str | None
    class Config:
        from_attributes = True
