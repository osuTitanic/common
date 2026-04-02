
from sqlalchemy.orm import mapped_column, Mapped, relationship
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

from datetime import datetime
from typing import List
from .beatmaps import DBBeatmapModding
from .users import DBUser
from .base import Base

class DBForum(Base):
    __tablename__ = "forums"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column('parent_id', Integer, ForeignKey('forums.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    name: Mapped[str] = mapped_column('name', String)
    description: Mapped[str] = mapped_column('description', String, default='')
    topic_count: Mapped[int] = mapped_column('topic_count', Integer, default=0)
    post_count: Mapped[int] = mapped_column('post_count', Integer, default=0)
    allow_icons: Mapped[bool] = mapped_column('allow_icons', Boolean, default=True)
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)

    parent: Mapped["DBForum"] = relationship('DBForum', back_populates='subforums', remote_side=[id])
    subforums: Mapped[List["DBForum"]] = relationship('DBForum', back_populates='parent')
    topics: Mapped[List["DBForumTopic"]] = relationship('DBForumTopic', back_populates='forum')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='forum')

class DBForumIcon(Base):
    __tablename__ = "forum_icons"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String)
    location: Mapped[str] = mapped_column('location', String)
    order: Mapped[int] = mapped_column('order', Integer, default=0)

    topics: Mapped[List["DBForumTopic"]] = relationship('DBForumTopic', back_populates='icon')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='icon')

class DBForumTopic(Base):
    __tablename__ = "forum_topics"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    forum_id: Mapped[int] = mapped_column('forum_id', Integer, ForeignKey('forums.id'))
    creator_id: Mapped[int] = mapped_column('creator_id', Integer, ForeignKey('users.id'))
    title: Mapped[str] = mapped_column('title', String)
    status_text: Mapped[str | None] = mapped_column('status_text', String, nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    last_post_at: Mapped[datetime] = mapped_column('last_post_at', DateTime, server_default=func.now())
    locked_at: Mapped[datetime | None] = mapped_column('locked_at', DateTime, nullable=True)
    views: Mapped[int] = mapped_column('views', Integer, default=0)
    post_count: Mapped[int] = mapped_column('post_count', Integer, default=0)
    icon_id: Mapped[int] = mapped_column('icon', Integer, ForeignKey('forum_icons.id'), nullable=True)
    can_change_icon: Mapped[bool] = mapped_column('can_change_icon', Boolean, default=True)
    can_star: Mapped[bool] = mapped_column('can_star', Boolean, default=False)
    announcement: Mapped[bool] = mapped_column('announcement', Boolean, default=False)
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)
    pinned: Mapped[bool] = mapped_column('pinned', Boolean, default=False)

    forum: Mapped["DBForum"] = relationship('DBForum', back_populates='topics')
    icon: Mapped["DBForumIcon"] = relationship('DBForumIcon', back_populates='topics')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='topic')
    stars: Mapped[List["DBForumStar"]] = relationship('DBForumStar', back_populates='topic')
    creator: Mapped["DBUser"] = relationship('DBUser', back_populates='created_topics')
    bookmarks: Mapped[List["DBForumBookmark"]] = relationship('DBForumBookmark', back_populates='topic')
    subscribers: Mapped[List["DBForumSubscriber"]] = relationship('DBForumSubscriber', back_populates='topic')

class DBForumStar(Base):
    __tablename__ = "forum_stars"

    topic_id: Mapped[int] = mapped_column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='starred_topics')
    topic: Mapped["DBForumTopic"] = relationship('DBForumTopic', back_populates='stars')

class DBForumPost(Base):
    __tablename__ = "forum_posts"

    id: Mapped[int] = mapped_column('id', BigInteger, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column('topic_id', Integer, ForeignKey('forum_topics.id'))
    forum_id: Mapped[int] = mapped_column('forum_id', Integer, ForeignKey('forums.id'))
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'))
    icon_id: Mapped[int] = mapped_column('icon_id', Integer, ForeignKey('forum_icons.id'), nullable=True)
    content: Mapped[str] = mapped_column('content', String)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    edit_time: Mapped[datetime] = mapped_column('edit_time', DateTime, server_default=func.now())
    edit_count: Mapped[int] = mapped_column('edit_count', Integer, default=0)
    edit_locked: Mapped[bool] = mapped_column('edit_locked', Boolean, default=False)
    hidden: Mapped[bool] = mapped_column('hidden', Boolean, default=False)
    draft: Mapped[bool] = mapped_column('draft', Boolean, default=False)
    deleted: Mapped[bool] = mapped_column('deleted', Boolean, default=False)

    modding: Mapped['DBBeatmapModding'] = relationship('DBBeatmapModding', back_populates='post')
    user: Mapped['DBUser'] = relationship('DBUser', back_populates='created_posts')
    icon: Mapped['DBForumIcon'] = relationship('DBForumIcon', back_populates='posts')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='posts')
    forum: Mapped['DBForum'] = relationship('DBForum', back_populates='posts')

class DBForumReport(Base):
    __tablename__ = "forum_reports"

    post_id: Mapped[int] = mapped_column('post_id', Integer, ForeignKey('forum_posts.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column('resolved_at', DateTime, nullable=True)
    reason: Mapped[str] = mapped_column('reason', String)

class DBForumBookmark(Base):
    __tablename__ = "forum_bookmarks"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    topic_id: Mapped[int] = mapped_column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='bookmarked_topics')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='bookmarks')

class DBForumSubscriber(Base):
    __tablename__ = "forum_subscribers"

    user_id: Mapped[int] = mapped_column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    topic_id: Mapped[int] = mapped_column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='subscribed_topics')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='subscribers')
