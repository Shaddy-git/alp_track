# backend/models/group.py
from datetime import date
from sqlalchemy import String, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db


# Промежуточная таблица для связи M:N «альпинисты ↔ группы»
group_members = db.Table(
    'group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role', db.String(20), default='member')
)


class Group(db.Model):
    """Группа альпинистов для совместного восхождения."""
    __tablename__ = 'groups'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Статус: planning / active / completed / cancelled
    status: Mapped[str] = mapped_column(String(20), default='planning')
    
    # Руководитель группы (инструктор)
    leader_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    # Связь M:N с пользователями
    members = relationship("User", secondary=group_members, back_populates="groups")
    
    ascents = relationship("Ascent", back_populates="group")
    
    def __repr__(self):
        return f'<Group {self.name} ({self.status})>'