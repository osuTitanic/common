
from datetime import datetime
from app.common.constants import GameMode
from sqlalchemy.orm import mapped_column, Mapped, relationship
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

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    name: Mapped[str] = mapped_column('name', String, primary_key=True)
    category: Mapped[str] = mapped_column('category', String)
    filename: Mapped[str] = mapped_column('filename', String)
    unlocked_at: Mapped[datetime] = mapped_column('unlocked_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='achievements')

class DBScore(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column('id', BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    beatmap_id: Mapped[int] = mapped_column('beatmap_id', Integer, ForeignKey('beatmaps.id'))
    client_version: Mapped[int] = mapped_column('client_version', Integer)
    client_string: Mapped[str] = mapped_column('client_version_string', String, default='')
    client_hash: Mapped[str | None] = mapped_column('client_hash', String, nullable=True)
    checksum: Mapped[str] = mapped_column('score_checksum', String)
    mode: Mapped[int] = mapped_column('mode', SmallInteger)
    pp: Mapped[float] = mapped_column('pp', Float)
    ppv1: Mapped[float] = mapped_column('ppv1', Float)
    acc: Mapped[float] = mapped_column('acc', Float)
    total_score: Mapped[int] = mapped_column('total_score', BigInteger)
    max_combo: Mapped[int] = mapped_column('max_combo', Integer)
    mods: Mapped[int] = mapped_column('mods', Integer)
    perfect: Mapped[bool] = mapped_column('perfect', Boolean)
    n300: Mapped[int] = mapped_column('n300', Integer)
    n100: Mapped[int] = mapped_column('n100', Integer)
    n50: Mapped[int] = mapped_column('n50', Integer)
    nMiss: Mapped[int] = mapped_column('nmiss', Integer)
    nGeki: Mapped[int] = mapped_column('ngeki', Integer)
    nKatu: Mapped[int] = mapped_column('nkatu', Integer)
    grade: Mapped[str] = mapped_column('grade', String, default='N')
    status_pp: Mapped[int] = mapped_column('status', SmallInteger, default=-1)
    status_score: Mapped[int] = mapped_column('status_score', SmallInteger, default=-1)
    pinned: Mapped[bool] = mapped_column('pinned', Boolean, default=False)
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)
    submitted_at: Mapped[datetime] = mapped_column('submitted_at', DateTime, server_default=func.now())
    failtime: Mapped[int | None] = mapped_column('failtime',  Integer, nullable=True)
    replay_md5: Mapped[str | None] = mapped_column('replay_md5', String, nullable=True)
    replay_views: Mapped[int] = mapped_column('replay_views', Integer, default=0)

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

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now(), primary_key=True)
    mode: Mapped[int] = mapped_column('mode', SmallInteger)
    rscore: Mapped[int] = mapped_column('rscore', BigInteger)
    pp: Mapped[int] = mapped_column('pp', Integer)
    ppv1: Mapped[int] = mapped_column('ppv1', Integer)
    global_rank: Mapped[int] = mapped_column('global_rank', Integer)
    country_rank: Mapped[int] = mapped_column('country_rank', Integer)
    score_rank: Mapped[int] = mapped_column('score_rank', Integer)
    ppv1_rank: Mapped[int] = mapped_column('ppv1_rank', Integer)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='rank_history')

class DBPlayHistory(Base):
    __tablename__ = "profile_play_history"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    mode: Mapped[int] = mapped_column('mode', SmallInteger, primary_key=True)
    year: Mapped[int] = mapped_column('year', Integer, primary_key=True)
    month: Mapped[int] = mapped_column('month', Integer, primary_key=True)
    plays: Mapped[int] = mapped_column('plays', Integer, default=0)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

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

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    mode: Mapped[int] = mapped_column('mode', SmallInteger, primary_key=True)
    year: Mapped[int] = mapped_column('year', Integer, primary_key=True)
    month: Mapped[int] = mapped_column('month', Integer, primary_key=True)
    replay_views: Mapped[int] = mapped_column('replay_views', Integer, default=0)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

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
