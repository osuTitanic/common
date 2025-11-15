
from datetime import datetime
from typing import List

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    SmallInteger,
    ForeignKey,
    DateTime,
    Boolean,
    Integer,
    Column,
    String,
    ARRAY
)

from .forums import DBForumTopic
from .users import DBUser
from .base import Base

class DBLogin(Base):
    __tablename__ = "logins"

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    time    = Column('time', DateTime, server_default=func.now(), primary_key=True)
    ip      = Column('ip', String)
    version = Column('osu_version', String)

    def __init__(
        self,
        user_id: int,
        ip: str,
        version: str
    ) -> None:
        self.user_id = user_id
        self.ip = ip
        self.version = version
        self.time = datetime.now()

class DBChannel(Base):
    __tablename__ = "channels"

    name              = Column('name', String, primary_key=True)
    topic             = Column('topic', String)
    read_permissions  = Column('read_permissions', Integer, default=1)
    write_permissions = Column('write_permissions', Integer, default=1)

    def __init__(self, name: str, topic: str, rp: int, wp: int) -> None:
        self.name = name
        self.topic = topic
        self.read_permissions = rp
        self.write_permissions = wp

class DBMessage(Base):
    __tablename__ = "messages"

    id      = Column('id', Integer, primary_key=True, autoincrement=True)
    sender  = Column('sender', String, ForeignKey('users.name'))
    target  = Column('target', String)
    message = Column('message', String)
    time    = Column('time', DateTime, server_default=func.now())

    def __init__(self, sender: str, target: str, message: str) -> None:
        self.message = message
        self.sender  = sender
        self.target  = target
        self.time    = datetime.now()

class DBDirectMessage(Base):
    __tablename__ = "direct_messages"

    id        = Column('id', Integer, primary_key=True, autoincrement=True)
    sender_id = Column('sender_id', Integer, ForeignKey('users.id'))
    target_id = Column('target_id', Integer, ForeignKey('users.id'))
    message   = Column('message', String)
    time      = Column('time', DateTime, server_default=func.now())
    read      = Column('read', Boolean, default=False)

class DBChatFilter(Base):
    __tablename__ = "filters"

    name                   = Column('name', String, primary_key=True)
    pattern                = Column('pattern', String, nullable=False)
    replacement            = Column('replacement', String, nullable=True)
    block                  = Column('block', Boolean, nullable=False, default=False)
    block_timeout_duration = Column('block_timeout_duration', Integer, nullable=True, default=None)
    created_at             = Column('created_at', DateTime, server_default=func.now())

class DBActivity(Base):
    __tablename__ = "profile_activity"

    id       = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id  = Column('user_id', Integer, ForeignKey('users.id'))
    time     = Column('time', DateTime, server_default=func.now())
    mode     = Column('mode', SmallInteger, nullable=True)
    type     = Column('type', SmallInteger, default=0)
    data     = Column('data', JSONB, default={})
    hidden   = Column('hidden', Boolean, default=False)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='activity')

class DBClient(Base):
    __tablename__ = "clients"

    user_id        = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    executable     = Column('executable', String, primary_key=True)
    adapters       = Column('adapters', String, primary_key=True)
    unique_id      = Column('unique_id', String, primary_key=True)
    disk_signature = Column('disk_signature', String, primary_key=True)
    banned         = Column('banned', Boolean, default=False)

    def __init__(
        self,
        user_id: int,
        executable: str,
        adapters: str,
        unique_id: str,
        disk_signature: str,
        banned: bool = False
    ) -> None:
        self.user_id = user_id
        self.executable = executable
        self.adapters = adapters
        self.unique_id = unique_id
        self.disk_signature = disk_signature
        self.banned = banned

class DBVerifiedClient(Base):
    __tablename__ = "clients_verified"

    type = Column('type', SmallInteger, primary_key=True)
    hash = Column('hash', String, primary_key=True)

class DBMatch(Base):
    __tablename__ = "mp_matches"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    bancho_id  = Column('bancho_id', SmallInteger)
    name       = Column('name', String)
    creator_id = Column('creator_id', Integer, ForeignKey('users.id'))
    created_at = Column('created_at', DateTime)
    ended_at   = Column('ended_at', DateTime, nullable=True)

    creator: Mapped["DBUser"] = relationship('DBUser', back_populates='matches')
    events: Mapped[List["DBMatchEvent"]] = relationship('DBMatchEvent', back_populates='match')

    def __init__(
        self,
        name: str,
        creator_id: int,
        bancho_id: int
    ) -> None:
        self.name = name
        self.bancho_id = bancho_id
        self.creator_id = creator_id
        self.created_at = datetime.now()

class DBMatchEvent(Base):
    __tablename__ = "mp_events"

    match_id = Column('match_id', Integer, ForeignKey('mp_matches.id'), primary_key=True)
    time     = Column('time', DateTime, server_default=func.now(), primary_key=True)
    type     = Column('type', SmallInteger)
    data     = Column('data', JSONB)

    match: Mapped["DBMatch"] = relationship('DBMatch', back_populates='events')

    def __init__(
        self,
        match_id: int,
        type: int,
        data: dict
    ) -> None:
        self.match_id = match_id
        self.type = type
        self.data = data

class DBUserCount(Base):
    __tablename__ = "user_count"

    time  = Column('time', DateTime, primary_key=True, server_default=func.now())
    count = Column('count', Integer, default=0)

    def __init__(self, count: int) -> None:
        self.time = datetime.now()
        self.count = count

class DBRelease(Base):
    __tablename__ = "releases"

    name        = Column('name', String, primary_key=True)
    version     = Column('version', Integer)
    description = Column('description', String, default='')
    category    = Column('category', String, default='Uncategorized')
    known_bugs  = Column('known_bugs', String, nullable=True)
    supported   = Column('supported', Boolean, default=True)
    preview     = Column('preview', Boolean, default=False)
    downloads   = Column('downloads', ARRAY(String), default=[])
    screenshots = Column('screenshots', ARRAY(String), default=[])
    hashes      = Column('hashes', JSONB, default=[])
    created_at  = Column('created_at', DateTime, server_default=func.now())

class DBModdedRelease(Base):
    __tablename__ = "releases_modding"

    name            = Column('name', String, primary_key=True)
    description     = Column('description', String)
    creator_id      = Column('creator_id', Integer, ForeignKey('users.id'))
    topic_id        = Column('topic_id', Integer, ForeignKey('forum_topics.id'))
    client_version  = Column('client_version', Integer)
    client_extension = Column('client_extension', String)
    downloads       = Column('downloads', ARRAY(String), default=[])
    screenshots     = Column('screenshots', ARRAY(String), default=[])
    hashes          = Column('hashes', JSONB, default=[])
    created_at      = Column('created_at', DateTime, server_default=func.now())

    creator: Mapped['DBUser'] = relationship('DBUser')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic')

class DBExtraRelease(Base):
    __tablename__ = "releases_extra"

    name        = Column('name', String, primary_key=True)
    description = Column('description', String)
    download    = Column('download', String)
    filename    = Column('filename', String)
