
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from datetime import datetime
from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    SmallInteger,
    ForeignKey,
    BigInteger,
    DateTime,
    Boolean,
    Integer,
    Column,
    String,
    Index,
    Float
)

import config
import app

Base = declarative_base()

class DBAchievement(Base):
    __tablename__ = "achievements"

    user_id     = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    name        = Column('name', String, primary_key=True)
    category    = Column('category', String)
    filename    = Column('filename', String)
    unlocked_at = Column('unlocked_at', DateTime, server_default=func.now())

    user = relationship('DBUser', back_populates='achievements', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, name: str, category: str, filename: str) -> None:
        self.category = category
        self.filename = filename
        self.user_id = user_id
        self.name = name

class DBStats(Base):
    __tablename__ = "stats"

    user_id      = Column('id', Integer, ForeignKey('users.id'), primary_key=True)
    mode         = Column('mode', SmallInteger, primary_key=True)

    rank         = Column('rank', Integer, default=0)
    tscore       = Column('tscore', BigInteger, default=0)
    rscore       = Column('rscore', BigInteger, default=0)
    pp           = Column('pp', Float, default=0.0)
    ppv1         = Column('ppv1', Float, default=0.0)
    playcount    = Column('playcount', BigInteger, default=0)
    playtime     = Column('playtime', Integer, default=0)
    acc          = Column('acc', Float, default=0.0)
    max_combo    = Column('max_combo', Integer, default=0)
    total_hits   = Column('total_hits', Integer, default=0)
    replay_views = Column('replay_views', Integer, default=0)

    xh_count  = Column('xh_count', Integer, default=0)
    x_count   = Column('x_count', Integer, default=0)
    sh_count  = Column('sh_count', Integer, default=0)
    s_count   = Column('s_count', Integer, default=0)
    a_count   = Column('a_count', Integer, default=0)
    b_count   = Column('b_count', Integer, default=0)
    c_count   = Column('c_count', Integer, default=0)
    d_count   = Column('d_count', Integer, default=0)

    Index('stats_id_idx', user_id)

    user = relationship('DBUser', back_populates='stats', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, mode: int) -> None:
        self.user_id = user_id
        self.mode    = mode

class DBScore(Base):
    __tablename__ = "scores"

    id             = Column('id', BigInteger, primary_key=True, autoincrement=True)
    user_id        = Column('user_id', Integer, ForeignKey('users.id'))
    beatmap_id     = Column('beatmap_id', Integer, ForeignKey('beatmaps.id'))
    client_version = Column('client_version', String)
    client_hash    = Column('client_hash', String)
    checksum       = Column('score_checksum', String)
    mode           = Column('mode', SmallInteger)
    pp             = Column('pp', Float)
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
    status         = Column('status', SmallInteger, default=-1)
    pinned         = Column('pinned', Boolean, default=False)
    submitted_at   = Column('submitted_at', DateTime, server_default=func.now())
    bad_flags      = Column('bad_flags', Integer, default=0)
    ac_flags       = Column('ac_flags', Integer, default=0)

    replay_md5     = Column('replay_md5', String, nullable=True)
    processes      = Column('processes',  String, nullable=True)
    failtime       = Column('failtime',  Integer, nullable=True)

    user    = relationship('DBUser', back_populates='scores', lazy='selectin', join_depth=2)
    beatmap = relationship('DBBeatmap', back_populates='scores', lazy='selectin', join_depth=2)

    Index('idx_beatmap_mode_status', beatmap_id, mode, status)
    Index('idx_beatmap_user_mode_status', beatmap_id, mode, user_id, status)

    def __init__(self, **kwargs) -> None:
        self.beatmap_id     = kwargs.get('beatmap_id')
        self.user_id        = kwargs.get('user_id')
        self.client_version = kwargs.get('client_version')
        self.client_hash    = kwargs.get('client_hash')
        self.checksum       = kwargs.get('score_checksum')
        self.mode           = kwargs.get('mode')
        self.pp             = kwargs.get('pp')
        self.acc            = kwargs.get('acc')
        self.total_score    = kwargs.get('total_score')
        self.max_combo      = kwargs.get('max_combo')
        self.mods           = kwargs.get('mods')
        self.perfect        = kwargs.get('perfect')
        self.n300           = kwargs.get('n300')
        self.n100           = kwargs.get('n100')
        self.n50            = kwargs.get('n50')
        self.nMiss          = kwargs.get('nMiss')
        self.nGeki          = kwargs.get('nGeki')
        self.nKatu          = kwargs.get('nKatu')
        self.grade          = kwargs.get('grade')
        self.status         = kwargs.get('status')
        self.processes      = kwargs.get('processes')
        self.failtime       = kwargs.get('failtime')
        self.replay_md5     = kwargs.get('replay_md5')

class DBPlay(Base):
    __tablename__ = "plays"

    user_id      = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    beatmap_id   = Column('beatmap_id', Integer, ForeignKey('beatmaps.id'), primary_key=True)
    set_id       = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    count        = Column('count', Integer)
    beatmap_file = Column('beatmap_file', String)

    user       = relationship('DBUser', back_populates='plays', lazy='selectin', join_depth=2)
    beatmap    = relationship('DBBeatmap', back_populates='plays', lazy='selectin', join_depth=2)
    beatmapset = relationship('DBBeatmapset', back_populates='plays', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, beatmap_id: int, set_id: int, beatmap_file: str, count: int = 1) -> None:
        self.beatmap_file = beatmap_file
        self.beatmap_id = beatmap_id
        self.user_id = user_id
        self.set_id = set_id
        self.count = count

class DBFavourite(Base):
    __tablename__ = "favourites"

    user_id    = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id     = Column('set_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user       = relationship('DBUser', back_populates='favourites', lazy='selectin', join_depth=2)
    beatmapset = relationship('DBBeatmapset', back_populates='favourites', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, set_id: int) -> None:
        self.user_id = user_id
        self.set_id  = set_id

class DBRating(Base):
    __tablename__ = "ratings"

    user_id      = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id       = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    map_checksum = Column('map_checksum', String, ForeignKey('beatmaps.md5'), primary_key=True)
    rating       = Column('rating', SmallInteger)

    user       = relationship('DBUser', back_populates='ratings', lazy='selectin', join_depth=2)
    beatmap    = relationship('DBBeatmap', back_populates='ratings', lazy='selectin', join_depth=2)
    beatmapset = relationship('DBBeatmapset', back_populates='ratings', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, set_id: int, map_checksum: str, rating: int) -> None:
        self.rating  = rating
        self.set_id  = set_id
        self.user_id = user_id
        self.map_checksum = map_checksum

class DBScreenshot(Base):
    __tablename__ = "screenshots"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id    = Column('user_id', ForeignKey('users.id'))
    created_at = Column('created_at', DateTime, server_default=func.now())
    hidden     = Column('hidden', Boolean, default=False)

    user = relationship('DBUser', back_populates='screenshots', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, hidden: bool):
        self.user_id = user_id
        self.hidden = hidden

class DBRelationship(Base):
    __tablename__ = "relationships"

    user_id   = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    target_id = Column('target_id', Integer, primary_key=True)
    status    = Column('status', SmallInteger)

    user = relationship('DBUser', back_populates='relationships', lazy='selectin', join_depth=2)

    def __init__(self, user: int, target: int, status: int) -> None:
        self.user_id = user
        self.target_id = target
        self.status = status

class DBComment(Base):
    __tablename__ = "comments"

    id          = Column('id', Integer, primary_key=True, autoincrement=True)
    target_id   = Column('target_id', Integer)
    target_type = Column('target_type', String)
    user_id     = Column('user_id', Integer, ForeignKey('users.id'))
    time        = Column('time', DateTime, server_default=func.now())
    comment     = Column('comment', String)
    format      = Column('format', String, nullable=True)
    mode        = Column('mode', SmallInteger, default=0)
    color       = Column('color', String, nullable=True)

    def __init__(self, target_id, target_type, user_id, time, comment, format = None, mode = 0, color = None) -> None:
        self.target_id   = target_id
        self.target_type = target_type
        self.user_id     = user_id
        self.time        = time
        self.comment     = comment
        self.format      = format
        self.mode        = mode
        self.color       = color

class DBLog(Base):
    __tablename__ = "logs"

    id      = Column('id', Integer, primary_key=True, autoincrement=True)
    level   = Column('level', String)
    type    = Column('type', String)
    message = Column('message', String)
    time    = Column('time', DateTime, server_default=func.now())

    def __init__(self, message: str, level: str, type: str) -> None:
        self.message = message
        self.level   = level
        self.type    = type
        self.time    = datetime.now()

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
    target  = Column('target', String) # Either channel or username
    message = Column('message', String)
    time    = Column('time', DateTime, server_default=func.now())

    def __init__(self, sender: str, target: str, message: str) -> None:
        self.message = message
        self.sender  = sender
        self.target  = target
        self.time    = datetime.now()

class DBBeatmapset(Base):
    __tablename__ = "beatmapsets"

    id                   = Column('id', Integer, primary_key=True, autoincrement=True)
    title                = Column('title', String, nullable=True)
    artist               = Column('artist', String, nullable=True)
    creator              = Column('creator', String, nullable=True)
    source               = Column('source', String, nullable=True)
    description          = Column('description', String, nullable=True)
    tags                 = Column('tags', String, nullable=True, default='')
    status               = Column('submission_status', Integer, default=3)
    has_video            = Column('has_video', Boolean, default=False)
    has_storyboard       = Column('has_storyboard', Boolean, default=False)
    server               = Column('server', SmallInteger, default=0)
    available            = Column('available', Boolean, default=True)
    created_at           = Column('submission_date', DateTime, server_default=func.now())
    approved_at          = Column('approved_date', DateTime, nullable=True)
    last_update          = Column('last_updated', DateTime, server_default=func.now())
    added_at             = Column('added_at', DateTime, nullable=True) # only if server is 0 (osu!)
    osz_filesize         = Column('osz_filesize', Integer, default=0)
    osz_filesize_novideo = Column('osz_filesize_novideo', Integer, default=0)
    language_id          = Column('language_id', SmallInteger, default=1)
    genre_id             = Column('genre_id', SmallInteger, default=1)

    Index('beatmapsets_id_idx', id)

    favourites = relationship('DBFavourite', back_populates='beatmapset', lazy='selectin', join_depth=2)
    beatmaps   = relationship('DBBeatmap', back_populates='beatmapset', lazy='selectin', join_depth=2)
    ratings    = relationship('DBRating', back_populates='beatmapset', lazy='selectin', join_depth=2)
    plays      = relationship('DBPlay', back_populates='beatmapset', lazy='selectin', join_depth=2)

    @property
    def full_name(self):
        return f'{self.artist} - {self.title} ({self.creator})'

    @property
    def link(self):
        name = self.full_name \
                   .replace('[', '(') \
                   .replace(']', ')')

        return f'[http://osu.{config.DOMAIN_NAME}/s/{self.id} {name}]'

    def __init__(
        self,
        id: int,
        title: str,
        artist: str,
        creator: str,
        source: str,
        tags: str,
        status: int,
        has_video: bool,
        has_storyboard: bool,
        created_at: datetime,
        approved_at: datetime,
        last_update: datetime,
        language_id: int,
        genre_id: int,
        osz_filesize: int,
        osz_filesize_novideo: int = 0,
        available: bool = True,
        server: int = 0
    ) -> None:
        self.id = id
        self.title = title
        self.artist = artist
        self.creator = creator
        self.source = source
        self.tags = tags
        self.status = status
        self.has_video = has_video
        self.has_storyboard = has_storyboard
        self.created_at = created_at
        self.approved_at = approved_at
        self.last_update = last_update
        self.language_id = language_id
        self.genre_id = genre_id
        self.osz_filesize = osz_filesize
        self.osz_filesize_novideo = osz_filesize_novideo
        self.available = available
        self.server = server
        self.added_at = datetime.now()

class DBBeatmap(Base):
    __tablename__ = "beatmaps"

    id           = Column('id', Integer, primary_key=True, autoincrement=True)
    set_id       = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    mode         = Column('mode', SmallInteger, default=0)
    md5          = Column('md5', String)
    status       = Column('status', SmallInteger, default=2)
    version      = Column('version', String)
    filename     = Column('filename', String)
    created_at   = Column('submission_date', DateTime, server_default=func.now())
    last_update  = Column('last_updated', DateTime, server_default=func.now())
    playcount    = Column('playcount', BigInteger, default=0)
    passcount    = Column('passcount', BigInteger, default=0)
    total_length = Column('total_length', Integer)

    max_combo = Column('max_combo', Integer)
    bpm       = Column('bpm',  Float, default=0.0)
    cs        = Column('cs',   Float, default=0.0)
    ar        = Column('ar',   Float, default=0.0)
    od        = Column('od',   Float, default=0.0)
    hp        = Column('hp',   Float, default=0.0)
    diff      = Column('diff', Float, default=0.0)

    Index('beatmaps_id_idx', id)
    Index('beatmaps_md5_idx', md5)
    Index('beatmaps_filename_idx', filename)

    beatmapset = relationship('DBBeatmapset', back_populates='beatmaps', lazy='selectin', join_depth=2)
    ratings    = relationship('DBRating', back_populates='beatmap', lazy='selectin', join_depth=2)
    scores     = relationship('DBScore', back_populates='beatmap', lazy='selectin', join_depth=2)
    plays      = relationship('DBPlay', back_populates='beatmap', lazy='selectin', join_depth=2)

    def __repr__(self) -> str:
        return f'<Beatmap ({self.id}) {self.beatmapset.artist} - {self.beatmapset.title} [{self.version}]>'

    @property
    def full_name(self):
        return f'{self.beatmapset.artist} - {self.beatmapset.title} [{self.version}]'

    @property
    def link(self):
        name = self.full_name \
                   .replace('[', '(') \
                   .replace(']', ')')

        return f'[http://osu.{config.DOMAIN_NAME}/b/{self.id} {name}]'

    @property
    def is_ranked(self) -> bool:
        return self.status > 0

    @property
    def awards_pp(self) -> bool:
        if config.APPROVED_MAP_REWARDS:
            return self.status > 0
        return self.status == 1

    @property
    def approved(self) -> bool:
        return self.status == 2

    def __init__(
        self,
        id: int,
        set_id: int,
        mode: int,
        md5: str,
        status: int,
        version: str,
        filename: str,
        created_at: datetime,
        last_update: datetime,
        total_length: int,
        max_combo: int,
        bpm: float,
        cs: float,
        ar: float,
        od: float,
        hp: float,
        diff: float
    ) -> None:
        self.id = id
        self.set_id = set_id
        self.mode = mode
        self.md5 = md5
        self.status = status
        self.version = version
        self.filename = filename
        self.created_at = created_at
        self.last_update = last_update
        self.total_length = total_length
        self.max_combo = max_combo
        self.bpm = bpm
        self.cs = cs
        self.ar = ar
        self.od = od
        self.hp = hp
        self.diff = diff

class DBBadge(Base):
    __tablename__ = "profile_badges"

    id                = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id           = Column('user_id', Integer, ForeignKey('users.id'))
    created           = Column('created', DateTime, server_default=func.now())
    badge_icon        = Column('badge_icon', String)
    badge_url         = Column('badge_url', String, nullable=True)
    badge_description = Column('badge_description', String, nullable=True)

    user = relationship('DBUser', back_populates='badges', lazy='selectin', join_depth=2)

class DBActivity(Base):
    __tablename__ = "profile_activity"

    id             = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id        = Column('user_id', Integer, ForeignKey('users.id'))
    time           = Column('time', DateTime, server_default=func.now())
    mode           = Column('mode', SmallInteger)
    activity_text  = Column('activity_text', String)
    activity_args  = Column('activity_args', String, nullable=True)
    activity_links = Column('activity_links', String, nullable=True)

    user = relationship('DBUser', back_populates='activity', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, mode: int, activity_text: str, activity_args: str, activity_links: str) -> None:
        self.user_id = user_id
        self.mode = mode
        self.activity_links = activity_links
        self.activity_text = activity_text
        self.activity_args = activity_args

class DBName(Base):
    __tablename__ = "name_history"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id    = Column('user_id', Integer, ForeignKey('users.id'))
    changed_at = Column('changed_at', DateTime, server_default=func.now())
    name       = Column('name', String)

    user = relationship('DBUser', back_populates='names', lazy='selectin', join_depth=2)

    def __init__(self, user_id: int, name: str) -> None:
        self.user_id = user_id
        self.name = name
        self.changed_at = datetime.now()

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

    user = relationship('DBUser', back_populates='rank_history', lazy='selectin', join_depth=2)

    def __init__(
        self,
        user_id: int,
        mode: int,
        rscore: int,
        pp: int,
        ppv1: int,
        global_rank: int,
        country_rank: int,
        score_rank: int,
        ppv1_rank: int
    ) -> None:
        self.user_id = user_id
        self.mode = mode
        self.rscore = rscore
        self.pp = pp
        self.ppv1 = ppv1
        self.global_rank = global_rank
        self.country_rank = country_rank
        self.score_rank = score_rank
        self.ppv1_rank = ppv1_rank
        self.time = datetime.now()

class DBPlayHistory(Base):
    __tablename__ = "profile_play_history"

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    mode    = Column('mode', SmallInteger, primary_key=True)
    year    = Column('year', Integer, primary_key=True)
    month   = Column('month', Integer, primary_key=True)
    plays   = Column('plays', Integer, default=0)

    user = relationship('DBUser', back_populates='play_history', lazy='selectin', join_depth=2)

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

    user = relationship('DBUser', back_populates='replay_history', lazy='selectin', join_depth=2)

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

class DBClient(Base):
    __tablename__ = "clients"

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    executable = Column('executable', String, primary_key=True)
    adapters = Column('adapters', String, primary_key=True)
    unique_id = Column('unique_id', String, primary_key=True)
    disk_signature = Column('disk_signature', String, primary_key=True)
    banned = Column('banned', Boolean, default=False)

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

class DBLogin(Base):
    __tablename__ = "logins"

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    time = Column('time', DateTime, server_default='now()', primary_key=True)
    ip = Column('ip', String)
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

class DBInfringement(Base):
    __tablename__ = "infringements"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    time = Column('time', DateTime, server_default='now()', primary_key=True)
    action = Column('action', SmallInteger, default=0) # 0: Ban 1: Mute
    length = Column('length', DateTime, nullable=True)
    is_permanent = Column('is_permanent', Boolean, default=False)
    description = Column('description', String, nullable=True)

    def __init__(
        self,
        user_id: int,
        action: int,
        length: datetime,
        description: Optional[str] = None,
        is_permanent: bool = False,
    ) -> None:
        self.user_id = user_id
        self.action = action
        self.length = length
        self.description = description
        self.is_permanent = is_permanent
        self.time = datetime.now()

class DBReport(Base):
    __tablename__ = "reports"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    target_id = Column('target_id', Integer, ForeignKey('users.id'))
    sender_id = Column('sender_id', Integer, ForeignKey('users.id'))
    time = Column('time', DateTime, server_default='now()')
    reason = Column('reason', String, nullable=True)
    resolved = Column('resolved', Boolean, default=False)

    # TODO: Relationships

    def __init__(
        self,
        target_id: int,
        sender_id: int,
        reason: Optional[str]
    ) -> None:
        self.target_id = target_id
        self.sender_id = sender_id
        self.reason = reason
        self.time = datetime.now()

class DBMatch(Base):
    __tablename__ = "mp_matches"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    bancho_id = Column('bancho_id', SmallInteger)
    name = Column('name', String)
    creator_id = Column('creator_id', Integer, ForeignKey('users.id'))
    created_at = Column('created_at', DateTime)
    ended_at = Column('ended_at', DateTime, nullable=True)

    creator = relationship('DBUser', back_populates='matches', lazy='selectin', join_depth=2)
    events = relationship('DBMatchEvent', back_populates='match', lazy='selectin', join_depth=2)

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
    time = Column('time', DateTime, server_default='now()', primary_key=True)
    type = Column('type', SmallInteger)
    data = Column('data', JSONB)

    match = relationship('DBMatch', back_populates='events', lazy='selectin', join_depth=2)

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

    time = Column('time', DateTime, primary_key=True, server_default='now()')
    count = Column('count', Integer, default=0)

    def __init__(self, count: int) -> None:
        self.time = datetime.now()
        self.count = count

class DBVerification(Base):
    __tablename__ = "verifications"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    token = Column('token', String)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    sent_at = Column('sent_at', DateTime, server_default='now()')
    type = Column('type', SmallInteger, default=0)

    user = relationship('DBUser', back_populates='verifications', lazy='selectin', join_depth=2)

    def __init__(
        self,
        token: str,
        user_id: int,
        type: int = 0
    ) -> None:
        self.token = token
        self.user_id = user_id
        self.type = type
        self.sent_at = datetime.now()

class DBUser(Base):
    __tablename__ = "users"

    id                 = Column('id', Integer, primary_key=True, autoincrement=True)
    name               = Column('name', String, unique=True)
    safe_name          = Column('safe_name', String, unique=True)
    email              = Column('email', String, unique=True)
    discord_id         = Column('discord_id', BigInteger, nullable=True, unique=True)
    bcrypt             = Column('pw', String)
    permissions        = Column('permissions', Integer, default=1)
    country            = Column('country', String)
    silence_end        = Column('silence_end', DateTime, nullable=True)
    supporter_end      = Column('supporter_end', DateTime, nullable=True)
    created_at         = Column('created_at', DateTime, server_default=func.now())
    latest_activity    = Column('latest_activity', DateTime, server_default=func.now())
    restricted         = Column('restricted', Boolean, default=False)
    activated          = Column('activated', Boolean, default=False)
    preferred_mode     = Column('preferred_mode', Integer, default=0)
    playstyle          = Column('playstyle', Integer, default=0)
    userpage_about     = Column('userpage_about', String, nullable=True)
    userpage_signature = Column('userpage_signature', String, nullable=True)
    userpage_banner    = Column('userpage_banner', String, nullable=True)
    userpage_website   = Column('userpage_website', String, nullable=True)
    userpage_discord   = Column('userpage_discord', String, nullable=True)
    userpage_twitter   = Column('userpage_twitter', String, nullable=True)
    userpage_location  = Column('userpage_location', String, nullable=True)
    userpage_interests = Column('userpage_interests', String, nullable=True)

    Index('users_id_idx', id)
    Index('users_name_idx', name)

    replay_history = relationship('DBReplayHistory', back_populates='user', lazy='selectin', join_depth=2)
    relationships  = relationship('DBRelationship', back_populates='user', lazy='selectin', join_depth=2)
    verifications  = relationship('DBVerification', back_populates='user', lazy='selectin', join_depth=2)
    rank_history   = relationship('DBRankHistory', back_populates='user', lazy='selectin', join_depth=2)
    play_history   = relationship('DBPlayHistory', back_populates='user', lazy='selectin', join_depth=2)
    achievements   = relationship('DBAchievement', back_populates='user', lazy='selectin', join_depth=2)
    screenshots    = relationship('DBScreenshot', back_populates='user', lazy='selectin', join_depth=2)
    favourites     = relationship('DBFavourite', back_populates='user', lazy='selectin', join_depth=2)
    activity       = relationship('DBActivity', back_populates='user', lazy='selectin', join_depth=2)
    ratings        = relationship('DBRating', back_populates='user', lazy='selectin', join_depth=2)
    scores         = relationship('DBScore', back_populates='user', lazy='selectin', join_depth=2)
    matches        = relationship('DBMatch', back_populates='creator', lazy='selectin', join_depth=2)
    stats          = relationship('DBStats', back_populates='user', lazy='selectin', join_depth=2)
    badges         = relationship('DBBadge', back_populates='user', lazy='selectin', join_depth=2)
    names          = relationship('DBName', back_populates='user', lazy='selectin', join_depth=2)
    plays          = relationship('DBPlay', back_populates='user', lazy='selectin', join_depth=2)

    def __init__(
        self,
        name: str,
        safe_name: str,
        email: str,
        bcrypt: str,
        country: str,
        activated: bool,
        discord_id: Optional[int],
        permissions: int = 1
    ) -> None:
        self.name = name
        self.safe_name = safe_name
        self.email = email
        self.bcrypt = bcrypt
        self.country = country
        self.activated = activated
        self.discord_id = discord_id
        self.permissions = permissions

    @property
    def link(self) -> str:
        return f'[http://osu.{config.DOMAIN_NAME}/u/{self.id} {self.name}]'

    @property
    def is_supporter(self) -> bool:
        if config.FREE_SUPPORTER:
            return True

        if self.remaining_supporter > 0:
            return True
        else:
            # Remove supporter
            self.supporter_end = None
            self.permissions -= 4

            # Update database
            instance = app.session.database.session
            instance.query(DBUser) \
                    .filter(DBUser.id == self.id) \
                    .update({
                        'supporter_end': None,
                        'permissions': self.permissions
                    })
            instance.commit()

        return False

    @property
    def remaining_supporter(self):
        if self.supporter_end:
            return self.supporter_end.timestamp() - datetime.now().timestamp()
        return 0

    # NOTE: These are required attributes for Flask-Login.
    #       I am not sure if you can implement them differently...

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
