
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship
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
from .users import DBUser
from .base import Base

class DBScreenshot(Base):
    __tablename__ = "screenshots"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id    = Column('user_id', ForeignKey('users.id'))
    created_at = Column('created_at', DateTime, server_default=func.now())
    hidden     = Column('hidden', Boolean, default=False)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='screenshots')

class DBLog(Base):
    __tablename__ = "logs"

    id      = Column('id', Integer, primary_key=True, autoincrement=True)
    level   = Column('level', String)
    type    = Column('type', String)
    message = Column('message', String)
    time    = Column('time', DateTime, server_default=func.now())

class DBBenchmark(Base):
    __tablename__ = "benchmarks"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id    = Column('user_id', Integer, ForeignKey('users.id'))
    smoothness = Column('smoothness', Float)
    framerate  = Column('framerate', Integer)
    score      = Column('score', BigInteger)
    grade      = Column('grade', String, default='N')
    created_at = Column('created_at', DateTime, server_default=func.now())
    client     = Column('client', String)
    hardware   = Column('hardware', JSONB)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='benchmarks')
