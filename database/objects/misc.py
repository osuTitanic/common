
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey,
    BigInteger,
    DateTime,
    Boolean,
    Integer,
    Column,
    String,
    Float
)

from datetime import datetime
from typing import Any
from .users import DBUser
from .base import Base

class DBScreenshot(Base):
    __tablename__ = "screenshots"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='screenshots')

class DBLog(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column('level', String)
    type: Mapped[str] = mapped_column('type', String)
    message: Mapped[str] = mapped_column('message', String)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())

class DBBenchmark(Base):
    __tablename__ = "benchmarks"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    smoothness: Mapped[float] = mapped_column('smoothness', Float)
    framerate: Mapped[int] = mapped_column('framerate', Integer)
    score: Mapped[int] = mapped_column('score', BigInteger)
    grade: Mapped[str] = mapped_column('grade', String, default='N')
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    client: Mapped[str] = mapped_column('client', String)
    hardware: Mapped[Any] = mapped_column('hardware', JSONB)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='benchmarks')
