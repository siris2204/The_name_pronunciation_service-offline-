# backend/app/models.py
from sqlalchemy import Column, Integer, String
from .db import Base

class Name(Base):
    __tablename__ = "names"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    audio_path = Column(String, nullable=True)
