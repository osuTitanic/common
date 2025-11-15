
from app.common.constants import GameMode
from datetime import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    SmallInteger,
    ForeignKey,
    BigInteger,
    DateTime,
    Boolean,
    Integer,
    Column,
    String,
    Float
)

from .beatmaps import DBBeatmap
from .users import DBUser
from .base import Base

class DBAchievement(Base):
    __tablename__ = "achievements"

    user_id     = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    name        = Column('name', String, primary_key=True)
    category    = Column('category', String)
    filename    = Column('filename', String)
    unlocked_at = Column('unlocked_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='achievements')

class DBScore(Base):
    __tablename__ = "scores"

    id             = Column('id', BigInteger, primary_key=True, autoincrement=True)
    user_id        = Column('user_id', Integer, ForeignKey('users.id'))
    beatmap_id     = Column('beatmap_id', Integer, ForeignKey('beatmaps.id'))
    client_version = Column('client_version', Integer)
    client_hash    = Column('client_hash', String, nullable=True)
    checksum       = Column('score_checksum', String)
    mode           = Column('mode', SmallInteger)
    pp             = Column('pp', Float)
    ppv1           = Column('ppv1', Float)
    acc            = Column('acc', Float)
    total_score    = Column('total_score', BigInteger)
    max_combo      = Column('max_combo', Integer)
    mods           = Column('mods', Integer)
    perfect        = Column('perfect', Boolean)
    n300           = Column('n300', Integer)
    n100           = Column('n100', Integer)
    n50            = Column('n50', Integer)
    nMiss          = Column('nmiss', Integer)
    nGeki          = Column('ngeki', Integer)
    nKatu          = Column('nkatu', Integer)
    grade          = Column('grade', String, default='N')
    status_pp      = Column('status', SmallInteger, default=-1)
    status_score   = Column('status_score', SmallInteger, default=-1)
    pinned         = Column('pinned', Boolean, default=False)
    hidden         = Column('hidden', Boolean, default=False)
    submitted_at   = Column('submitted_at', DateTime, server_default=func.now())
    failtime       = Column('failtime',  Integer, nullable=True)
    replay_md5     = Column('replay_md5', String, nullable=True)
    replay_views   = Column('replay_views', Integer, default=0)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='scores')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='scores')

    @property
    def passed(self) -> bool:
        return self.failtime is None
    
    @property
    def relaxing(self) -> bool:
        return (self.mods & 1 << 7) > 0 or (self.mods & 1 << 13) > 0

    @property
    def total_hits(self) -> int:
        if self.mode in (GameMode.OsuMania, GameMode.Taiko):
            return self.n50 + self.n100 + self.n00 + self.nGeki + self.nKatu

        return self.n50 + self.n100 + self.n300

    @property
    def total_objects(self) -> int:
        if self.mode in (GameMode.Osu, GameMode.Taiko):
            return self.n50 + self.n100 + self.n300 + self.nMiss

        elif self.mode == GameMode.CatchTheBeat:
            return self.n50 + self.n100 + self.n300 + self.nKatu + self.nMiss

        return self.n50 + self.n100 + self.n300 + self.nGeki + self.nKatu + self.nMiss

class DBRankHistory(Base):
    __tablename__ = "profile_rank_history"

    user_id      = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    time         = Column('time', DateTime, server_default=func.now(), primary_key=True)
    mode         = Column('mode', SmallInteger)
    rscore       = Column('rscore', BigInteger)
    pp           = Column('pp', Integer)
    ppv1         = Column('ppv1', Integer)
    global_rank  = Column('global_rank', Integer)
    country_rank = Column('country_rank', Integer)
    score_rank   = Column('score_rank', Integer)
    ppv1_rank    = Column('ppv1_rank', Integer)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='rank_history')

class DBPlayHistory(Base):
    __tablename__ = "profile_play_history"

    user_id    = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    mode       = Column('mode', SmallInteger, primary_key=True)
    year       = Column('year', Integer, primary_key=True)
    month      = Column('month', Integer, primary_key=True)
    plays      = Column('plays', Integer, default=0)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='play_history')

    def __init__(
        self,
        user_id: int,
        mode: int,
        plays: int = 0
    ) -> None:
        time = datetime.now()
        self.user_id = user_id
        self.mode  = mode
        self.plays = plays
        self.year  = time.year
        self.month = time.month

class DBReplayHistory(Base):
    __tablename__ = "profile_replay_history"

    user_id      = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    mode         = Column('mode', SmallInteger, primary_key=True)
    year         = Column('year', Integer, primary_key=True)
    month        = Column('month', Integer, primary_key=True)
    replay_views = Column('replay_views', Integer, default=0)
    created_at   = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='replay_history')

    def __init__(
        self,
        user_id: int,
        mode: int,
        replay_views: int = 0
    ) -> None:
        time = datetime.now()
        self.replay_views = replay_views
        self.user_id = user_id
        self.year  = time.year
        self.month = time.month
        self.mode  = mode
