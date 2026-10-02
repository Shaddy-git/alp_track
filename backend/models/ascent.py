# backend/models/ascent.py
from datetime import date
from sqlalchemy import Date, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db


class Ascent(db.Model):
    """Факт восхождения альпиниста на гору."""
    __tablename__ = 'ascents'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    mountain_id: Mapped[int] = mapped_column(ForeignKey('mountains.id'), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=True)
    
    ascent_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    user = relationship("User", backref="ascents")
    mountain = relationship("Mountain", back_populates="ascents")
    group = relationship("Group", back_populates="ascents")
    
    def __repr__(self):
        return f'<Ascent user={self.user_id} mountain={self.mountain_id}>'