
from datetime import datetime
from typing import List

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey,
    BigInteger,
    DateTime,
    Boolean,
    Integer,
    Column,
    String
)

from .beatmaps import DBBeatmapModding
from .users import DBUser
from .base import Base

class DBForum(Base):
    __tablename__ = "forums"

    id          = Column('id', Integer, primary_key=True, autoincrement=True)
    parent_id   = Column('parent_id', Integer, ForeignKey('forums.id'), nullable=True)
    created_at  = Column('created_at', DateTime, server_default=func.now())
    name        = Column('name', String)
    description = Column('description', String, default='')
    topic_count = Column('topic_count', Integer, default=0)
    post_count  = Column('post_count', Integer, default=0)
    allow_icons = Column('allow_icons', Boolean, default=True)
    hidden      = Column('hidden', Boolean, default=False)

    parent: Mapped["DBForum"] = relationship('DBForum', back_populates='subforums', remote_side=[id])
    subforums: Mapped[List["DBForum"]] = relationship('DBForum', back_populates='parent')
    topics: Mapped[List["DBForumTopic"]] = relationship('DBForumTopic', back_populates='forum')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='forum')

class DBForumIcon(Base):
    __tablename__ = "forum_icons"

    id       = Column('id', Integer, primary_key=True, autoincrement=True)
    name     = Column('name', String)
    location = Column('location', String)
    order    = Column('order', Integer, default=0)

    topics: Mapped[List["DBForumTopic"]] = relationship('DBForumTopic', back_populates='icon')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='icon')

class DBForumTopic(Base):
    __tablename__ = "forum_topics"

    id              = Column('id', Integer, primary_key=True, autoincrement=True)
    forum_id        = Column('forum_id', Integer, ForeignKey('forums.id'))
    creator_id      = Column('creator_id', Integer, ForeignKey('users.id'))
    title           = Column('title', String)
    status_text     = Column('status_text', String, nullable=True)
    created_at      = Column('created_at', DateTime, server_default=func.now())
    last_post_at    = Column('last_post_at', DateTime, server_default=func.now())
    locked_at       = Column('locked_at', DateTime, nullable=True)
    views           = Column('views', Integer, default=0)
    post_count      = Column('post_count', Integer, default=0)
    icon_id         = Column('icon', Integer, ForeignKey('forum_icons.id'), nullable=True)
    can_change_icon = Column('can_change_icon', Boolean, default=True)
    can_star        = Column('can_star', Boolean, default=False)
    announcement    = Column('announcement', Boolean, default=False)
    hidden          = Column('hidden', Boolean, default=False)
    pinned          = Column('pinned', Boolean, default=False)

    forum: Mapped["DBForum"] = relationship('DBForum', back_populates='topics')
    icon: Mapped["DBForumIcon"] = relationship('DBForumIcon', back_populates='topics')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='topic')
    stars: Mapped[List["DBForumStar"]] = relationship('DBForumStar', back_populates='topic')
    creator: Mapped["DBUser"] = relationship('DBUser', back_populates='created_topics')
    bookmarks: Mapped[List["DBForumBookmark"]] = relationship('DBForumBookmark', back_populates='topic')
    subscribers: Mapped[List["DBForumSubscriber"]] = relationship('DBForumSubscriber', back_populates='topic')

class DBForumStar(Base):
    __tablename__ = "forum_stars"

    topic_id   = Column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)
    user_id    = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='starred_topics')
    topic: Mapped["DBForumTopic"] = relationship('DBForumTopic', back_populates='stars')

class DBForumPost(Base):
    __tablename__ = "forum_posts"

    id          = Column('id', BigInteger, primary_key=True, autoincrement=True)
    topic_id    = Column('topic_id', Integer, ForeignKey('forum_topics.id'))
    forum_id    = Column('forum_id', Integer, ForeignKey('forums.id'))
    user_id     = Column('user_id', Integer, ForeignKey('users.id'))
    icon_id     = Column('icon_id', Integer, ForeignKey('forum_icons.id'), nullable=True)
    content     = Column('content', String)
    created_at  = Column('created_at', DateTime, server_default=func.now())
    edit_time   = Column('edit_time', DateTime, server_default=func.now())
    edit_count  = Column('edit_count', Integer, default=0)
    edit_locked = Column('edit_locked', Boolean, default=False)
    hidden      = Column('hidden', Boolean, default=False)
    draft       = Column('draft', Boolean, default=False)
    deleted     = Column('deleted', Boolean, default=False)

    modding: Mapped['DBBeatmapModding'] = relationship('DBBeatmapModding', back_populates='post')
    user: Mapped['DBUser'] = relationship('DBUser', back_populates='created_posts')
    icon: Mapped['DBForumIcon'] = relationship('DBForumIcon', back_populates='posts')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='posts')
    forum: Mapped['DBForum'] = relationship('DBForum', back_populates='posts')

class DBForumReport(Base):
    __tablename__ = "forum_reports"

    post_id     = Column('post_id', Integer, ForeignKey('forum_posts.id'), primary_key=True)
    user_id     = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at  = Column('created_at', DateTime, server_default=func.now())
    resolved_at = Column('resolved_at', DateTime, nullable=True)
    reason      = Column('reason', String)

class DBForumBookmark(Base):
    __tablename__ = "forum_bookmarks"

    user_id  = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    topic_id = Column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='bookmarked_topics')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='bookmarks')

class DBForumSubscriber(Base):
    __tablename__ = "forum_subscribers"

    user_id  = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    topic_id = Column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='subscribed_topics')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='subscribers')
