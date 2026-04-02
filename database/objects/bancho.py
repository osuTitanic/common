
from datetime import datetime
from typing import List, Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    SmallInteger,
    ForeignKey,
    DateTime,
    Boolean,
    Integer,
    Column,
    String
)

from .users import DBUser
from .base import Base

class DBLogin(Base):
    __tablename__ = "logins"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now(), primary_key=True)
    ip: Mapped[str] = mapped_column('ip', String)
    version: Mapped[str] = mapped_column('osu_version', String)

class DBChannel(Base):
    __tablename__ = "channels"

    name: Mapped[str] = mapped_column('name', String, primary_key=True)
    topic: Mapped[str] = mapped_column('topic', String)
    read_permissions: Mapped[int] = mapped_column('read_permissions', Integer, default=1)
    write_permissions: Mapped[int] = mapped_column('write_permissions', Integer, default=1)

class DBMessage(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    sender: Mapped[str] = mapped_column('sender', String, ForeignKey('users.name'))
    target: Mapped[str] = mapped_column('target', String)
    message: Mapped[str] = mapped_column('message', String)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())

class DBDirectMessage(Base):
    __tablename__ = "direct_messages"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column('sender_id', Integer, ForeignKey('users.id'))
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('users.id'))
    message: Mapped[str] = mapped_column('message', String)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())
    read: Mapped[bool] = mapped_column('read', Boolean, default=False)

class DBChatFilter(Base):
    __tablename__ = "filters"

    name: Mapped[str] = mapped_column('name', String, primary_key=True)
    pattern: Mapped[str] = mapped_column('pattern', String, nullable=False)
    replacement: Mapped[str | None] = mapped_column('replacement', String, nullable=True)
    block: Mapped[bool] = mapped_column('block', Boolean, nullable=False, default=False)
    block_timeout_duration: Mapped[int | None] = mapped_column('block_timeout_duration', Integer, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

class DBActivity(Base):
    __tablename__ = "profile_activity"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())
    mode: Mapped[int | None] = mapped_column('mode', SmallInteger, nullable=True)
    type: Mapped[int] = mapped_column('type', SmallInteger, default=0)
    data: Mapped[Any] = mapped_column('data', JSONB, default={})
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='activity')

class DBClient(Base):
    __tablename__ = "clients"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    executable: Mapped[str] = mapped_column('executable', String, primary_key=True)
    adapters: Mapped[str] = mapped_column('adapters', String, primary_key=True)
    unique_id: Mapped[str] = mapped_column('unique_id', String, primary_key=True)
    disk_signature: Mapped[str] = mapped_column('disk_signature', String, primary_key=True)
    banned: Mapped[bool] = mapped_column('banned', Boolean, default=False)

class DBVerifiedClient(Base):
    __tablename__ = "clients_verified"

    type: Mapped[int] = mapped_column('type', SmallInteger, primary_key=True)
    hash: Mapped[str] = mapped_column('hash', String, primary_key=True)

class DBMatch(Base):
    __tablename__ = "mp_matches"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    bancho_id: Mapped[int] = mapped_column('bancho_id', SmallInteger)
    name: Mapped[str] = mapped_column('name', String)
    creator_id: Mapped[int] = mapped_column('creator_id', Integer, ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime)
    ended_at: Mapped[datetime | None] = mapped_column('ended_at', DateTime, nullable=True)

    creator: Mapped["DBUser"] = relationship('DBUser', back_populates='matches')
    events: Mapped[List["DBMatchEvent"]] = relationship('DBMatchEvent', back_populates='match')

class DBMatchEvent(Base):
    __tablename__ = "mp_events"

    match_id: Mapped[int] = mapped_column('match_id', Integer, ForeignKey('mp_matches.id'), primary_key=True)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now(), primary_key=True)
    type: Mapped[int] = mapped_column('type', SmallInteger)
    data: Mapped[Any] = mapped_column('data', JSONB)

    match: Mapped["DBMatch"] = relationship('DBMatch', back_populates='events')

class DBUserActivity(Base):
    __tablename__ = "user_activity"

    time: Mapped[datetime] = mapped_column('time', DateTime, primary_key=True, server_default=func.now())
    osu_count: Mapped[int] = mapped_column('osu_count', Integer, default=0)
    irc_count: Mapped[int] = mapped_column('irc_count', Integer, default=0)
    mp_count: Mapped[int] = mapped_column('mp_count', Integer, default=0)

    @property
    def total_users(self) -> int:
        return self.osu_count + self.irc_count
