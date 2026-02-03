
from typing import List, TYPE_CHECKING
from app.common.config import config_instance as config

from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, relationship, deferred
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

    id                   = Column('id', Integer, primary_key=True, autoincrement=True)
    title                = Column('title', String, nullable=True)
    title_unicode        = Column('title_unicode', String, nullable=True)
    artist               = Column('artist', String, nullable=True)
    artist_unicode       = Column('artist_unicode', String, nullable=True)
    source               = Column('source', String, nullable=True)
    source_unicode       = Column('source_unicode', String, nullable=True)
    creator              = Column('creator', String, nullable=True)
    display_title        = Column('display_title', String, nullable=True)
    description          = Column('description', String, nullable=True)
    tags                 = Column('tags', String, nullable=True, default='')
    status               = Column('submission_status', Integer, default=3)
    has_video            = Column('has_video', Boolean, default=False)
    has_storyboard       = Column('has_storyboard', Boolean, default=False)
    server               = Column('server', SmallInteger, default=0)
    download_server      = Column('download_server', SmallInteger, default=0)
    topic_id             = Column('topic_id', Integer, nullable=True)
    creator_id           = Column('creator_id', Integer, ForeignKey('users.id'), nullable=True)
    available            = Column('available', Boolean, default=True)
    enhanced             = Column('enhanced', Boolean, default=False)
    explicit             = Column('explicit', Boolean, default=False)
    created_at           = Column('submission_date', DateTime, server_default=func.now())
    approved_at          = Column('approved_date', DateTime, nullable=True)
    approved_by          = Column('approved_by', Integer, ForeignKey('users.id'), nullable=True)
    last_update          = Column('last_updated', DateTime, server_default=func.now())
    added_at             = Column('added_at', DateTime, nullable=True, server_default=func.now())
    total_playcount      = Column('total_playcount', BigInteger, default=0)
    max_diff             = Column('max_diff', Float, default=0.0)
    rating_average       = Column('rating_average', Float, default=0.0)
    rating_count         = Column('rating_count', Integer, default=0)
    favourite_count      = Column('favourite_count', Integer, default=0)
    osz_filesize         = Column('osz_filesize', Integer, default=0)
    osz_filesize_novideo = Column('osz_filesize_novideo', Integer, default=0)
    language_id          = Column('language_id', SmallInteger, default=1)
    genre_id             = Column('genre_id', SmallInteger, default=1)
    star_priority        = Column('star_priority', Integer, default=0)
    offset               = Column('offset', Integer, default=0)
    meta_hash            = Column('meta_hash', String, nullable=True)
    info_hash            = Column('info_hash', String, nullable=True)
    body_hash            = Column('body_hash', String, nullable=True)

    # Full-text search
    search = deferred(Column('search', TSVECTOR, Computed(
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
    search_text = deferred(Column('search_text', String, Computed(
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

    id            = Column('id', Integer, primary_key=True, autoincrement=True)
    set_id        = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    mode          = Column('mode', SmallInteger, default=0)
    md5           = Column('md5', String)
    status        = Column('status', SmallInteger, default=2)
    version       = Column('version', String)
    filename      = Column('filename', String)
    created_at    = Column('submission_date', DateTime, server_default=func.now())
    last_update   = Column('last_updated', DateTime, server_default=func.now())
    playcount     = Column('playcount', BigInteger, default=0)
    passcount     = Column('passcount', BigInteger, default=0)
    total_length  = Column('total_length', Integer)
    drain_length  = Column('drain_length', Integer, default=0)
    count_normal  = Column('count_normal', Integer, default=0)
    count_slider  = Column('count_slider', Integer, default=0)
    count_spinner = Column('count_spinner', Integer, default=0)

    max_combo         = Column('max_combo', Integer)
    bpm               = Column('bpm',Float, default=0.0)
    cs                = Column('cs', Float, default=0.0)
    ar                = Column('ar', Float, default=0.0)
    od                = Column('od', Float, default=0.0)
    hp                = Column('hp', Float, default=0.0)
    diff              = Column('diff', Float, default=0.0)
    diff_eyup         = Column('diff_eyup', Float, default=0.0)
    slider_multiplier = Column('slider_multiplier', Float, default=0.0)

    search = deferred(Column('search', TSVECTOR, Computed(
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

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    beatmap_id = Column('beatmap_id', Integer, ForeignKey('beatmaps.id'), primary_key=True)
    is_beatmap_author = Column('is_beatmap_author', Boolean, default=False)
    allow_resource_updates = Column('allow_resource_updates', Boolean, default=False)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='collaborations')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='collaborations')

class DBBeatmapCollaborationRequest(Base):
    __tablename__ = "beatmap_collaboration_requests"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    target_id = Column('target_id', Integer, ForeignKey('users.id'))
    beatmap_id = Column('beatmap_id', Integer, ForeignKey('beatmaps.id'))
    allow_resource_updates = Column('allow_resource_updates', Boolean, default=False)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[user_id])
    target: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[target_id])
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='collaboration_requests')

class DBBeatmapCollaborationBlacklist(Base):
    __tablename__ = "beatmap_collaboration_blacklist"

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    target_id = Column('target_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[user_id])
    target: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[target_id])

class DBBeatmapNomination(Base):
    __tablename__ = "beatmap_nominations"

    user_id   = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id    = Column('set_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    time      = Column('time', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='nominations')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='nominations')

class DBBeatmapModding(Base):
    __tablename__ = "beatmap_modding"

    id        = Column('id', Integer, primary_key=True, autoincrement=True)
    target_id = Column('target_id', Integer, ForeignKey('users.id'))
    sender_id = Column('sender_id', Integer, ForeignKey('users.id'))
    set_id    = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    post_id   = Column('post_id', Integer, ForeignKey('forum_posts.id'))
    amount    = Column('amount', Integer, default=0)
    time      = Column('time', DateTime, server_default=func.now())

    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='modding')
    post: Mapped["DBForumPost"] = relationship('DBForumPost', back_populates='modding')
    target: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[target_id])
    sender: Mapped["DBUser"] = relationship('DBUser', foreign_keys=[sender_id])

class DBBeatmapPack(Base):
    __tablename__ = "beatmap_packs"

    id            = Column('id', Integer, primary_key=True, autoincrement=True)
    name          = Column('name', String)
    category      = Column('category', String)
    download_link = Column('download_link', String)
    description   = Column('description', String, default='')
    creator_id    = Column('creator_id', Integer, ForeignKey('users.id'))
    created_at    = Column('created_at', DateTime, server_default=func.now())
    updated_at    = Column('updated_at', DateTime, server_default=func.now())

    entries: Mapped[List['DBBeatmapPackEntry']] = relationship('DBBeatmapPackEntry', back_populates='pack')
    creator: Mapped['DBUser'] = relationship('DBUser')

class DBBeatmapPackEntry(Base):
    __tablename__ = "beatmap_pack_entries"

    pack_id = Column('pack_id', Integer, ForeignKey('beatmap_packs.id'), primary_key=True)
    beatmapset_id = Column('beatmapset_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    pack: Mapped['DBBeatmapPack'] = relationship('DBBeatmapPack', back_populates='entries')
    beatmapset: Mapped['DBBeatmapset'] = relationship('DBBeatmapset')

class DBPlay(Base):
    __tablename__ = "plays"

    user_id      = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    beatmap_id   = Column('beatmap_id', Integer, ForeignKey('beatmaps.id'), primary_key=True)
    set_id       = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    count        = Column('count', Integer)
    beatmap_file = Column('beatmap_file', String)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='plays')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='plays')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='plays')

class DBFavourite(Base):
    __tablename__ = "favourites"

    user_id    = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id     = Column('set_id', Integer, ForeignKey('beatmapsets.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='favourites')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='favourites')

class DBRating(Base):
    __tablename__ = "ratings"

    user_id      = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    set_id       = Column('set_id', Integer, ForeignKey('beatmapsets.id'))
    map_checksum = Column('map_checksum', String, ForeignKey('beatmaps.md5'), primary_key=True)
    rating       = Column('rating', SmallInteger)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='ratings')
    beatmap: Mapped["DBBeatmap"] = relationship('DBBeatmap', back_populates='ratings')
    beatmapset: Mapped["DBBeatmapset"] = relationship('DBBeatmapset', back_populates='ratings')

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

class DBResourceMirror(Base):
    __tablename__ = "resource_mirrors"

    url      = Column('url', String, primary_key=True)
    type     = Column('type', Integer)
    server   = Column('server', Integer)
    priority = Column('priority', Integer, default=0)
