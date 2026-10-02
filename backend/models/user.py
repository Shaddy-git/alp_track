# backend/models/user.py
from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db


class User(db.Model):
    """Пользователь системы: альпинист, инструктор или администратор."""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    
    # ВАЖНО: хранится только хеш пароля, никогда сам пароль!
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Роль: climber / instructor / admin
    role: Mapped[str] = mapped_column(String(20), default='climber', nullable=False)
    
    # Уровень подготовки: 1 (новичок) — 5 (эксперт)
    experience_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связь M:N с группами через промежуточную таблицу
    groups = relationship("Group", secondary="group_members", back_populates="members")
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'