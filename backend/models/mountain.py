# backend/models/mountain.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db


class Mountain(db.Model):
    """Гора — объект восхождения."""
    __tablename__ = 'mountains'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    
    # Категория сложности: 1 — 5
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False)
    
    ascents = relationship("Ascent", back_populates="mountain")
    
    def __repr__(self):
        return f'<Mountain {self.name} ({self.height}m)>'