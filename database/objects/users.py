
from typing import List, TYPE_CHECKING
from app.common.config import config_instance as config

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

    user_id      = Column('id', Integer, ForeignKey('users.id'), primary_key=True)
    mode         = Column('mode', SmallInteger, primary_key=True)

    rank         = Column('rank', Integer, default=0)
    peak_rank    = Column('peak_rank', Integer, default=0)
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

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='stats')

class DBRelationship(Base):
    __tablename__ = "relationships"

    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    target_id = Column('target_id', Integer, ForeignKey('users.id'), primary_key=True)
    status = Column('status', SmallInteger)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='relationships', foreign_keys=[user_id])
    target: Mapped["DBUser"] = relationship('DBUser', back_populates='target_relationships', foreign_keys=[target_id])

class DBBadge(Base):
    __tablename__ = "profile_badges"

    id                = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id           = Column('user_id', Integer, ForeignKey('users.id'))
    created           = Column('created', DateTime, server_default=func.now())
    badge_icon        = Column('badge_icon', String)
    badge_url         = Column('badge_url', String, nullable=True)
    badge_description = Column('badge_description', String, nullable=True)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='badges')

class DBName(Base):
    __tablename__ = "name_history"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    name       = Column('name', String)
    user_id    = Column('user_id', Integer, ForeignKey('users.id'))
    reserved   = Column('reserved', Boolean, default=True)
    changed_at = Column('changed_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='names')

class DBInfringement(Base):
    __tablename__ = "infringements"

    id           = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id      = Column('user_id', Integer, ForeignKey('users.id'))
    time         = Column('time', DateTime, server_default=func.now(), primary_key=True)
    action       = Column('action', SmallInteger, default=0) # 0: Ban 1: Mute
    length       = Column('length', DateTime, nullable=True)
    is_permanent = Column('is_permanent', Boolean, default=False)
    description  = Column('description', String, nullable=True)

class DBReport(Base):
    __tablename__ = "reports"

    id        = Column('id', Integer, primary_key=True, autoincrement=True)
    target_id = Column('target_id', Integer, ForeignKey('users.id'))
    sender_id = Column('sender_id', Integer, ForeignKey('users.id'))
    time      = Column('time', DateTime, server_default=func.now())
    reason    = Column('reason', String, nullable=True)
    resolved  = Column('resolved', Boolean, default=False)

class DBVerification(Base):
    __tablename__ = "verifications"

    id      = Column('id', Integer, primary_key=True, autoincrement=True)
    token   = Column('token', String)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    sent_at = Column('sent_at', DateTime, server_default=func.now())
    type    = Column('type', SmallInteger, default=0)

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='verifications')

class DBGroup(Base):
    __tablename__ = "groups"

    id                 = Column('id', Integer, primary_key=True, autoincrement=True)
    name               = Column('name', String)
    short_name         = Column('short_name', String)
    description        = Column('description', String, nullable=True)
    color              = Column('color', String)
    bancho_permissions = Column('bancho_permissions', SmallInteger, nullable=True, default=0)
    hidden             = Column('hidden', Boolean, default=False)

    permissions: Mapped[List["DBGroupPermission"]] = relationship('DBGroupPermission', back_populates='group')
    entries: Mapped[List["DBGroupEntry"]] = relationship('DBGroupEntry', back_populates='group')

class DBGroupEntry(Base):
    __tablename__ = "groups_entries"

    group_id = Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
    user_id  = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)

    group: Mapped["DBGroup"] = relationship('DBGroup', back_populates='entries')
    user: Mapped["DBUser"] = relationship('DBUser', back_populates='groups')

class DBUserPermission(Base):
    __tablename__ = "user_permissions"

    id          = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id     = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    permission  = Column('permission', String)
    rejected    = Column('rejected', Boolean, default=False)
    created_at  = Column('created_at', DateTime, server_default=func.now())
    updated_at  = Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='permissions')

class DBGroupPermission(Base):
    __tablename__ = "group_permissions"

    id          = Column('id', Integer, primary_key=True, autoincrement=True)
    group_id    = Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
    permission  = Column('permission', String)
    rejected    = Column('rejected', Boolean, default=False)
    created_at  = Column('created_at', DateTime, server_default=func.now())
    updated_at  = Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())

    group: Mapped["DBGroup"] = relationship('DBGroup', back_populates='permissions')

class DBNotification(Base):
    __tablename__ = "notifications"

    id      = Column('id', BigInteger, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    type    = Column('type', SmallInteger)
    header  = Column('header', String)
    content = Column('content', String)
    link    = Column('link', String)
    read    = Column('read', Boolean, default=False)
    time    = Column('time', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='notifications')

class DBUser(Base):
    __tablename__ = "users"

    id                 = Column('id', Integer, primary_key=True, autoincrement=True)
    name               = Column('name', String, unique=True)
    safe_name          = Column('safe_name', String, unique=True)
    email              = Column('email', String, unique=True)
    discord_id         = Column('discord_id', BigInteger, nullable=True, unique=True)
    bcrypt             = Column('pw', String)
    is_bot             = Column('bot', Boolean, default=False)
    country            = Column('country', String)
    silence_end        = Column('silence_end', DateTime, nullable=True)
    created_at         = Column('created_at', DateTime, server_default=func.now())
    latest_activity    = Column('latest_activity', DateTime, server_default=func.now())
    restricted         = Column('restricted', Boolean, default=False)
    activated          = Column('activated', Boolean, default=False)
    preferred_mode     = Column('preferred_mode', Integer, default=0)
    preferred_ranking  = Column('preferred_ranking', String, default='global')
    playstyle          = Column('playstyle', Integer, default=0)
    irc_token          = Column('irc_token', String, server_default="encode(gen_random_bytes(5), 'hex')")
    avatar_hash        = Column('avatar_hash', String, nullable=True)
    avatar_last_update = Column('avatar_last_changed', DateTime, server_default=func.now())
    friendonly_dms     = Column('friendonly_dms', Boolean, default=False)
    userpage           = Column('userpage_about', String, nullable=True)
    signature          = Column('userpage_signature', String, nullable=True)
    title              = Column('userpage_title', String, nullable=True)
    banner             = Column('userpage_banner', String, nullable=True)
    website            = Column('userpage_website', String, nullable=True)
    discord            = Column('userpage_discord', String, nullable=True)
    twitter            = Column('userpage_twitter', String, nullable=True)
    location           = Column('userpage_location', String, nullable=True)
    interests          = Column('userpage_interests', String, nullable=True)

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
