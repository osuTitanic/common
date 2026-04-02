
from app.common.config import config_instance as config
from typing import List, TYPE_CHECKING
from datetime import datetime

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

from .base import Base

if TYPE_CHECKING:
    from .beatmaps import *
    from .rankings import *
    from .bancho import *
    from .forums import *
    from .misc import *

import app.common

class DBStats(Base):
    __tablename__ = "stats"

    user_id: Mapped[int] = mapped_column('id', Integer, ForeignKey('users.id'), primary_key=True)
    mode: Mapped[int] = mapped_column('mode', SmallInteger, primary_key=True)

    rank: Mapped[int] = mapped_column('rank', Integer, default=0)
    peak_rank: Mapped[int] = mapped_column('peak_rank', Integer, default=0)
    tscore: Mapped[int] = mapped_column('tscore', BigInteger, default=0)
    rscore: Mapped[int] = mapped_column('rscore', BigInteger, default=0)
    pp: Mapped[float] = mapped_column('pp', Float, default=0.0)
    ppv1: Mapped[float] = mapped_column('ppv1', Float, default=0.0)
    playcount: Mapped[int] = mapped_column('playcount', BigInteger, default=0)
    playtime: Mapped[int] = mapped_column('playtime', Integer, default=0)
    acc: Mapped[float] = mapped_column('acc', Float, default=0.0)
    max_combo: Mapped[int] = mapped_column('max_combo', Integer, default=0)
    total_hits: Mapped[int] = mapped_column('total_hits', Integer, default=0)
    replay_views: Mapped[int] = mapped_column('replay_views', Integer, default=0)

    xh_count: Mapped[int] = mapped_column('xh_count', Integer, default=0)
    x_count: Mapped[int] = mapped_column('x_count', Integer, default=0)
    sh_count: Mapped[int] = mapped_column('sh_count', Integer, default=0)
    s_count: Mapped[int] = mapped_column('s_count', Integer, default=0)
    a_count: Mapped[int] = mapped_column('a_count', Integer, default=0)
    b_count: Mapped[int] = mapped_column('b_count', Integer, default=0)
    c_count: Mapped[int] = mapped_column('c_count', Integer, default=0)
    d_count: Mapped[int] = mapped_column('d_count', Integer, default=0)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='stats')

class DBRelationship(Base):
    __tablename__ = "relationships"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('users.id'), primary_key=True)
    status: Mapped[int] = mapped_column('status', SmallInteger)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='relationships', foreign_keys=[user_id])
    target: Mapped["DBUser"] = relationship('DBUser', back_populates='target_relationships', foreign_keys=[target_id])

class DBBadge(Base):
    __tablename__ = "profile_badges"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    created: Mapped[datetime] = mapped_column('created', DateTime, server_default=func.now())
    badge_icon: Mapped[str] = mapped_column('badge_icon', String)
    badge_url: Mapped[str | None] = mapped_column('badge_url', String, nullable=True)
    badge_description: Mapped[str | None] = mapped_column('badge_description', String, nullable=True)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='badges')

class DBName(Base):
    __tablename__ = "name_history"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    reserved: Mapped[bool] = mapped_column('reserved', Boolean, default=True)
    changed_at: Mapped[datetime] = mapped_column('changed_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='names')

class DBInfringement(Base):
    __tablename__ = "infringements"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now(), primary_key=True)
    action: Mapped[int] = mapped_column('action', SmallInteger, default=0) # 0: Ban 1: Mute
    length: Mapped[datetime | None] = mapped_column('length', DateTime, nullable=True)
    is_permanent: Mapped[bool] = mapped_column('is_permanent', Boolean, default=False)
    description: Mapped[str | None] = mapped_column('description', String, nullable=True)

class DBReport(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('users.id'))
    sender_id: Mapped[int] = mapped_column('sender_id', Integer, ForeignKey('users.id'))
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())
    reason: Mapped[str | None] = mapped_column('reason', String, nullable=True)
    resolved: Mapped[bool] = mapped_column('resolved', Boolean, default=False)

class DBVerification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column('token', String)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    sent_at: Mapped[datetime] = mapped_column('sent_at', DateTime, server_default=func.now())
    type: Mapped[int] = mapped_column('type', SmallInteger, default=0)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='verifications')

class DBGroup(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String)
    short_name: Mapped[str] = mapped_column('short_name', String)
    description: Mapped[str | None] = mapped_column('description', String, nullable=True)
    color: Mapped[str] = mapped_column('color', String)
    bancho_permissions: Mapped[int | None] = mapped_column('bancho_permissions', SmallInteger, nullable=True, default=0)
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)

    permissions: Mapped[List["DBGroupPermission"]] = relationship('DBGroupPermission', back_populates='group')
    entries: Mapped[List["DBGroupEntry"]] = relationship('DBGroupEntry', back_populates='group')

class DBGroupEntry(Base):
    __tablename__ = "groups_entries"

    group_id: Mapped[int] = mapped_column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)

    group: Mapped["DBGroup"] = relationship('DBGroup', back_populates='entries')
    user: Mapped["DBUser"] = relationship('DBUser', back_populates='groups')

class DBUserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    permission: Mapped[str] = mapped_column('permission', String)
    rejected: Mapped[bool] = mapped_column('rejected', Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='permissions')

class DBGroupPermission(Base):
    __tablename__ = "group_permissions"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
    permission: Mapped[str] = mapped_column('permission', String)
    rejected: Mapped[bool] = mapped_column('rejected', Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())

    group: Mapped["DBGroup"] = relationship('DBGroup', back_populates='permissions')

class DBNotification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column('id', BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    type: Mapped[int] = mapped_column('type', SmallInteger)
    header: Mapped[str] = mapped_column('header', String)
    content: Mapped[str] = mapped_column('content', String)
    link: Mapped[str] = mapped_column('link', String)
    read: Mapped[bool] = mapped_column('read', Boolean, default=False)
    time: Mapped[datetime] = mapped_column('time', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='notifications')

class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String, unique=True)
    safe_name: Mapped[str] = mapped_column('safe_name', String, unique=True)
    email: Mapped[str] = mapped_column('email', String, unique=True)
    discord_id: Mapped[int | None] = mapped_column('discord_id', BigInteger, nullable=True, unique=True)
    bcrypt: Mapped[str] = mapped_column('pw', String)
    is_bot: Mapped[bool] = mapped_column('bot', Boolean, default=False)
    country: Mapped[str] = mapped_column('country', String)
    silence_end: Mapped[datetime | None] = mapped_column('silence_end', DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    latest_activity: Mapped[datetime] = mapped_column('latest_activity', DateTime, server_default=func.now())
    restricted: Mapped[bool] = mapped_column('restricted', Boolean, default=False)
    activated: Mapped[bool] = mapped_column('activated', Boolean, default=False)
    preferred_mode: Mapped[int] = mapped_column('preferred_mode', Integer, default=0)
    preferred_ranking: Mapped[str] = mapped_column('preferred_ranking', String, default='global')
    playstyle: Mapped[int] = mapped_column('playstyle', Integer, default=0)
    irc_token: Mapped[str] = mapped_column('irc_token', String, server_default="encode(gen_random_bytes(5), 'hex')")
    avatar_hash: Mapped[str | None] = mapped_column('avatar_hash', String, nullable=True)
    avatar_last_update: Mapped[datetime] = mapped_column('avatar_last_changed', DateTime, server_default=func.now())
    friendonly_dms: Mapped[bool] = mapped_column('friendonly_dms', Boolean, default=False)
    userpage: Mapped[str | None] = mapped_column('userpage_about', String, nullable=True)
    signature: Mapped[str | None] = mapped_column('userpage_signature', String, nullable=True)
    title: Mapped[str | None] = mapped_column('userpage_title', String, nullable=True)
    banner: Mapped[str | None] = mapped_column('userpage_banner', String, nullable=True)
    website: Mapped[str | None] = mapped_column('userpage_website', String, nullable=True)
    discord: Mapped[str | None] = mapped_column('userpage_discord', String, nullable=True)
    twitter: Mapped[str | None] = mapped_column('userpage_twitter', String, nullable=True)
    location: Mapped[str | None] = mapped_column('userpage_location', String, nullable=True)
    interests: Mapped[str | None] = mapped_column('userpage_interests', String, nullable=True)

    target_relationships: Mapped[List['DBRelationship']] = relationship('DBRelationship', back_populates='target', foreign_keys='DBRelationship.target_id')
    relationships: Mapped[List['DBRelationship']] = relationship('DBRelationship', back_populates='user', foreign_keys='DBRelationship.user_id')
    collaborations: Mapped[List['DBBeatmapCollaboration']] = relationship('DBBeatmapCollaboration', back_populates='user')
    replay_history: Mapped[List['DBReplayHistory']] = relationship('DBReplayHistory', back_populates='user')
    nominations: Mapped[List['DBBeatmapNomination']] = relationship('DBBeatmapNomination', back_populates='user')
    bookmarked_topics: Mapped[List['DBForumBookmark']] = relationship('DBForumBookmark', back_populates='user')
    subscribed_topics: Mapped[List['DBForumSubscriber']] = relationship('DBForumSubscriber', back_populates='user')
    verifications: Mapped[List['DBVerification']] = relationship('DBVerification', back_populates='user')
    notifications: Mapped[List['DBNotification']] = relationship('DBNotification', back_populates='user')
    created_topics: Mapped[List['DBForumTopic']] = relationship('DBForumTopic', back_populates='creator')
    starred_topics: Mapped[List['DBForumStar']] = relationship('DBForumStar', back_populates='user')
    created_posts: Mapped[List['DBForumPost']] = relationship('DBForumPost', back_populates='user')
    permissions: Mapped[List['DBUserPermission']] = relationship('DBUserPermission', back_populates='user')
    rank_history: Mapped[List['DBRankHistory']] = relationship('DBRankHistory', back_populates='user')
    play_history: Mapped[List['DBPlayHistory']] = relationship('DBPlayHistory', back_populates='user')
    achievements: Mapped[List['DBAchievement']] = relationship('DBAchievement', back_populates='user')
    screenshots: Mapped[List['DBScreenshot']] = relationship('DBScreenshot', back_populates='user')
    favourites: Mapped[List['DBFavourite']] = relationship('DBFavourite', back_populates='user')
    benchmarks: Mapped[List['DBBenchmark']] = relationship('DBBenchmark', back_populates='user')
    activity: Mapped[List['DBActivity']] = relationship('DBActivity', back_populates='user')
    groups: Mapped[List['DBGroupEntry']] = relationship('DBGroupEntry', back_populates='user')
    matches: Mapped[List['DBMatch']] = relationship('DBMatch', back_populates='creator')
    ratings: Mapped[List['DBRating']] = relationship('DBRating', back_populates='user')
    scores: Mapped[List['DBScore']] = relationship('DBScore', back_populates='user')
    badges: Mapped[List['DBBadge']] = relationship('DBBadge', back_populates='user')
    stats: Mapped[List['DBStats']] = relationship('DBStats', back_populates='user')
    names: Mapped[List['DBName']] = relationship('DBName', back_populates='user')
    plays: Mapped[List['DBPlay']] = relationship('DBPlay', back_populates='user')

    def __repr__(self) -> str:
        return f'<DBUser "{self.name}" ({self.id})>'

    @property
    def url(self) -> str:
        return f'http://osu.{config.DOMAIN_NAME}/u/{self.id}'

    @property
    def link(self) -> str:
        return f'[{self.url} {self.name}]'

    @property
    def avatar_filename(self) -> str:
        return f'{self.id}_{self.avatar_hash or "unknown"}.png'

    @property
    def rankings(self) -> dict:
        return app.common.cache.leaderboards.player_rankings_all_modes(self.id, self.country)

    @property
    def group_ids(self):
        return [group.group_id for group in self.groups]

    @property
    def is_admin(self) -> bool:
        return self.check_groups([1, 2])

    @property
    def is_bat(self) -> bool:
        return self.check_groups([1, 2, 3])

    @property
    def is_moderator(self) -> bool:
        return self.check_groups([1, 2, 4])

    @property
    def has_preview_access(self) -> bool:
        return self.check_groups([1, 2, 997])

    @property
    def is_verified(self) -> bool:
        return self.check_groups([1, 2, 998])

    @property
    def is_supporter(self) -> bool:
        return self.check_groups([1, 2, 999])

    @property
    def is_donator(self) -> bool:
        return 6 in self.group_ids

    def check_groups(self, ids: List[int]) -> bool:
        return any(group in self.group_ids for group in ids)

    """Required attributes for Flask-Login"""

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.id
