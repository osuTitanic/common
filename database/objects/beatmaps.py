
from app.common.config import config_instance as config
from typing import Any, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import mapped_column, Mapped, relationship, deferred
from sqlalchemy.sql import func
from sqlalchemy import (
    SmallInteger,
    ForeignKey,
    BigInteger,
    Computed,
    DateTime,
    Boolean,
    Integer,
    Column,
    String,
    Float
)

from .base import Base

if TYPE_CHECKING:
    from .forums import DBForumPost
    from .rankings import DBScore
    from .users import DBUser

class DBBeatmapset(Base):
    __tablename__ = "beatmapsets"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column('title', String, nullable=True)
    title_unicode: Mapped[str | None] = mapped_column('title_unicode', String, nullable=True)
    artist: Mapped[str | None] = mapped_column('artist', String, nullable=True)
    artist_unicode: Mapped[str | None] = mapped_column('artist_unicode', String, nullable=True)
    source: Mapped[str | None] = mapped_column('source', String, nullable=True)
    source_unicode: Mapped[str | None] = mapped_column('source_unicode', String, nullable=True)
    creator: Mapped[str | None] = mapped_column('creator', String, nullable=True)
    display_title: Mapped[str | None] = mapped_column('display_title', String, nullable=True)
    description: Mapped[str | None] = mapped_column('description', String, nullable=True)
    tags: Mapped[str | None] = mapped_column('tags', String, nullable=True, default='')
    status: Mapped[int] = mapped_column('submission_status', Integer, default=3)
    has_video: Mapped[bool] = mapped_column('has_video', Boolean, default=False)
    has_storyboard: Mapped[bool] = mapped_column('has_storyboard', Boolean, default=False)
    server: Mapped[int] = mapped_column('server', SmallInteger, default=0)
    download_server: Mapped[int] = mapped_column('download_server', SmallInteger, default=0)
    topic_id: Mapped[int | None] = mapped_column('topic_id', Integer, nullable=True)
    creator_id: Mapped[int] = mapped_column('creator_id', Integer, ForeignKey('users.id'), nullable=True)
    available: Mapped[bool] = mapped_column('available', Boolean, default=True)
    enhanced: Mapped[bool] = mapped_column('enhanced', Boolean, default=False)
    explicit: Mapped[bool] = mapped_column('explicit', Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column('submission_date', DateTime, server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column('approved_date', DateTime, nullable=True)
    approved_by: Mapped[int] = mapped_column('approved_by', Integer, ForeignKey('users.id'), nullable=True)
    last_update: Mapped[datetime] = mapped_column('last_updated', DateTime, server_default=func.now())
    added_at: Mapped[datetime | None] = mapped_column('added_at', DateTime, nullable=True, server_default=func.now())
    total_playcount: Mapped[int] = mapped_column('total_playcount', BigInteger, default=0)
    max_diff: Mapped[float] = mapped_column('max_diff', Float, default=0.0)
    rating_average: Mapped[float] = mapped_column('rating_average', Float, default=0.0)
    rating_count: Mapped[int] = mapped_column('rating_count', Integer, default=0)
    favourite_count: Mapped[int] = mapped_column('favourite_count', Integer, default=0)
    osz_filesize: Mapped[int] = mapped_column('osz_filesize', Integer, default=0)
    osz_filesize_novideo: Mapped[int] = mapped_column('osz_filesize_novideo', Integer, default=0)
    language_id: Mapped[int] = mapped_column('language_id', SmallInteger, default=1)
    genre_id: Mapped[int] = mapped_column('genre_id', SmallInteger, default=1)
    star_priority: Mapped[int] = mapped_column('star_priority', Integer, default=0)
    offset: Mapped[int] = mapped_column('offset', Integer, default=0)
    meta_hash: Mapped[str | None] = mapped_column('meta_hash', String, nullable=True)
    info_hash: Mapped[str | None] = mapped_column('info_hash', String, nullable=True)
    body_hash: Mapped[str | None] = mapped_column('body_hash', String, nullable=True)

    # Full-text search
    search: Mapped[Any] = deferred(mapped_column('search', TSVECTOR, Computed(
        "setweight(to_tsvector('simple', coalesce(title, '')), 'B') || "
        "setweight(to_tsvector('simple', coalesce(title_unicode, '')), 'A') || "
        "setweight(to_tsvector('simple', coalesce(artist, '')), 'B') || "
        "setweight(to_tsvector('simple', coalesce(artist_unicode, '')), 'A') || "
        "setweight(to_tsvector('simple', coalesce(creator, '')), 'B') || "
        "setweight(to_tsvector('simple', coalesce(source, '')), 'B') || "
        "setweight(to_tsvector('simple', coalesce(tags, '')), 'B')",
        persisted=True
    )))

    # Trigram / fuzzy search
    search_text: Mapped[str] = deferred(mapped_column('search_text', String, Computed(
        "coalesce(title, '') || ' ' || "
        "coalesce(title_unicode, '') || ' ' || "
        "coalesce(artist, '') || ' ' || "
        "coalesce(artist_unicode, '') || ' ' || "
        "coalesce(creator, '') || ' ' || "
        "coalesce(source, '') || ' ' || "
        "coalesce(tags, '')",
        persisted=True
    )))

    creator_user: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[creator_id])
    nominations: Mapped[List["DBBeatmapNomination"]] = relationship('DBBeatmapNomination', back_populates='beatmapset')
    modding: Mapped[List["DBBeatmapModding"]] = relationship('DBBeatmapModding', back_populates='beatmapset')
    favourites: Mapped[List["DBFavourite"]] = relationship('DBFavourite', back_populates='beatmapset')
    beatmaps: Mapped[List["DBBeatmap"]] = relationship('DBBeatmap', back_populates='beatmapset')
    ratings: Mapped[List["DBRating"]] = relationship('DBRating', back_populates='beatmapset')
    plays: Mapped[List["DBPlay"]] = relationship('DBPlay', back_populates='beatmapset')

    @property
    def full_name(self):
        return f'{self.artist} - {self.title} ({self.creator})'

    @property
    def osz2_hashes(self) -> str:
        return f"{self.body_hash}{self.meta_hash}".upper()

    @property
    def link(self):
        return (
            f'[http://osu.{config.DOMAIN_NAME}/s/{self.id} '
            f'{self.full_name.replace("[", "(").replace("]", ")")}]'
        )

class DBBeatmap(Base):
    __tablename__ = "beatmaps"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    set_id: Mapped[int] = mapped_column('set_id', Integer, ForeignKey('beatmapsets.id'))
    mode: Mapped[int] = mapped_column('mode', SmallInteger, default=0)
    md5: Mapped[str] = mapped_column('md5', String)
    status: Mapped[int] = mapped_column('status', SmallInteger, default=2)
    version: Mapped[str] = mapped_column('version', String)
    filename: Mapped[str] = mapped_column('filename', String)
    created_at: Mapped[datetime] = mapped_column('submission_date', DateTime, server_default=func.now())
    last_update: Mapped[datetime] = mapped_column('last_updated', DateTime, server_default=func.now())
    playcount: Mapped[int] = mapped_column('playcount', BigInteger, default=0)
    passcount: Mapped[int] = mapped_column('passcount', BigInteger, default=0)
    total_length: Mapped[int] = mapped_column('total_length', Integer)
    drain_length: Mapped[int] = mapped_column('drain_length', Integer, default=0)
    count_normal: Mapped[int] = mapped_column('count_normal', Integer, default=0)
    count_slider: Mapped[int] = mapped_column('count_slider', Integer, default=0)
    count_spinner: Mapped[int] = mapped_column('count_spinner', Integer, default=0)

    max_combo: Mapped[int] = mapped_column('max_combo', Integer)
    bpm: Mapped[float] = mapped_column('bpm',Float, default=0.0)
    cs: Mapped[float] = mapped_column('cs', Float, default=0.0)
    ar: Mapped[float] = mapped_column('ar', Float, default=0.0)
    od: Mapped[float] = mapped_column('od', Float, default=0.0)
    hp: Mapped[float] = mapped_column('hp', Float, default=0.0)
    diff: Mapped[float] = mapped_column('diff', Float, default=0.0)
    diff_eyup: Mapped[float] = mapped_column('diff_eyup', Float, default=0.0)
    slider_multiplier: Mapped[float] = mapped_column('slider_multiplier', Float, default=0.0)

    search: Mapped[Any] = deferred(mapped_column('search', TSVECTOR, Computed(
        "to_tsvector('simple', coalesce(version, ''))",
        persisted=True
    )))

    collaboration_requests: Mapped[List["DBBeatmapCollaborationRequest"]] = relationship('DBBeatmapCollaborationRequest', back_populates='beatmap')
    collaborations: Mapped[List["DBBeatmapCollaboration"]] = relationship('DBBeatmapCollaboration', back_populates='beatmap')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='beatmaps')
    ratings: Mapped[List["DBRating"]] = relationship('DBRating', back_populates='beatmap')
    scores: Mapped[List["DBScore"]] = relationship('DBScore', back_populates='beatmap')
    plays: Mapped[List["DBPlay"]] = relationship('DBPlay', back_populates='beatmap')

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
    def approved(self) -> bool:
        return self.status == 2

    @property
    def awards_pp(self) -> bool:
        if config.APPROVED_MAP_REWARDS:
            return self.status > 0
        return self.status in (1, 2)

class DBBeatmapCollaboration(Base):
    __tablename__ = "beatmap_collaboration"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    beatmap_id: Mapped[int] = mapped_column('beatmap_id', Integer, ForeignKey('beatmaps.id'), primary_key=True)
    is_beatmap_author: Mapped[bool] = mapped_column('is_beatmap_author', Boolean, default=False)
    allow_resource_updates: Mapped[bool] = mapped_column('allow_resource_updates', Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='collaborations')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='collaborations')

class DBBeatmapCollaborationRequest(Base):
    __tablename__ = "beatmap_collaboration_requests"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('users.id'))
    beatmap_id: Mapped[int] = mapped_column('beatmap_id', Integer, ForeignKey('beatmaps.id'))
    allow_resource_updates: Mapped[bool] = mapped_column('allow_resource_updates', Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[user_id])
    target: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[target_id])
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='collaboration_requests')

class DBBeatmapCollaborationBlacklist(Base):
    __tablename__ = "beatmap_collaboration_blacklist"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[user_id])
    target: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[target_id])

class DBBeatmapNomination(Base):
    __tablename__ = "beatmap_nominations"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id: Mapped[int] = mapped_column('set_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='nominations')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='nominations')

class DBBeatmapModding(Base):
    __tablename__ = "beatmap_modding"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('users.id'))
    sender_id: Mapped[int] = mapped_column('sender_id', Integer, ForeignKey('users.id'))
    set_id: Mapped[int] = mapped_column('set_id', Integer, ForeignKey('beatmapsets.id'))
    post_id: Mapped[int] = mapped_column('post_id', Integer, ForeignKey('forum_posts.id'))
    amount: Mapped[int] = mapped_column('amount', Integer, default=0)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())

    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='modding')
    post: Mapped["DBForumPost"] = relationship('DBForumPost', back_populates='modding')
    target: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[target_id])
    sender: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[sender_id])

class DBBeatmapPack(Base):
    __tablename__ = "beatmap_packs"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String)
    category: Mapped[str] = mapped_column('category', String)
    download_link: Mapped[str] = mapped_column('download_link', String)
    description: Mapped[str] = mapped_column('description', String, default='')
    creator_id: Mapped[int] = mapped_column('creator_id', Integer, ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column('updated_at', DateTime, server_default=func.now())

    entries: Mapped[List['DBBeatmapPackEntry']] = relationship('DBBeatmapPackEntry', back_populates='pack')
    creator: Mapped['DBUser'] = relationship('DBUser')

class DBBeatmapPackEntry(Base):
    __tablename__ = "beatmap_pack_entries"

    pack_id: Mapped[int] = mapped_column('pack_id', Integer, ForeignKey('beatmap_packs.id'), primary_key=True)
    beatmapset_id: Mapped[int] = mapped_column('beatmapset_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    pack: Mapped['DBBeatmapPack'] = relationship('DBBeatmapPack', back_populates='entries')
    beatmapset: Mapped['DBBeatmapset'] = relationship('DBBeatmapset')

class DBPlay(Base):
    __tablename__ = "plays"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    beatmap_id: Mapped[int] = mapped_column('beatmap_id', Integer, ForeignKey('beatmaps.id'), primary_key=True)
    set_id: Mapped[int] = mapped_column('set_id', Integer, ForeignKey('beatmapsets.id'))
    count: Mapped[int] = mapped_column('count', Integer)
    beatmap_file: Mapped[str] = mapped_column('beatmap_file', String)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='plays')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='plays')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='plays')

class DBFavourite(Base):
    __tablename__ = "favourites"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id: Mapped[int] = mapped_column('set_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='favourites')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='favourites')

class DBRating(Base):
    __tablename__ = "ratings"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id: Mapped[int] = mapped_column('set_id', Integer, ForeignKey('beatmapsets.id'))
    map_checksum: Mapped[str] = mapped_column('map_checksum', String, ForeignKey('beatmaps.md5'), primary_key=True)
    rating: Mapped[int] = mapped_column('rating', SmallInteger)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='ratings')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='ratings')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='ratings')

class DBComment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int] = mapped_column('target_id', Integer)
    target_type: Mapped[str] = mapped_column('target_type', String)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())
    comment: Mapped[str] = mapped_column('comment', String)
    format: Mapped[str | None] = mapped_column('format', String, nullable=True)
    mode: Mapped[int] = mapped_column('mode', SmallInteger, default=0)
    color: Mapped[str | None] = mapped_column('color', String, nullable=True)

    def __init__(self, target_id, target_type, user_id, time, comment, format = None, mode = 0, color = None) -> None:
        self.target_id   = target_id
        self.target_type = target_type
        self.user_id     = user_id
        self.time        = time
        self.comment     = comment
        self.format      = format
        self.mode        = mode
        self.color       = color

class DBResourceMirror(Base):
    __tablename__ = "resource_mirrors"

    url: Mapped[str] = mapped_column('url', String, primary_key=True)
    type: Mapped[int] = mapped_column('type', Integer)
    server: Mapped[int] = mapped_column('server', Integer)
    priority: Mapped[int] = mapped_column('priority', Integer, default=0)
