
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
    allow_icons = Column('allow_icons', Boolean, default=True)
    hidden      = Column('hidden', Boolean, default=False)

    parent: Mapped["DBForum"] = relationship('DBForum', back_populates='subforums', remote_side=[id])
    subforums: Mapped[List["DBForum"]] = relationship('DBForum', back_populates='parent')
    topics: Mapped[List["DBForumTopic"]] = relationship('DBForumTopic', back_populates='forum')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='forum')

    def __init__(
        self,
        name: str,
        description: str,
        hidden: bool,
        parent_id: int | None
    ) -> None:
        self.name = name
        self.description = description
        self.hidden = hidden
        self.parent_id = parent_id

class DBForumIcon(Base):
    __tablename__ = "forum_icons"

    id       = Column('id', Integer, primary_key=True, autoincrement=True)
    name     = Column('name', String)
    location = Column('location', String)
    order    = Column('order', Integer, default=0)

    topics: Mapped[List["DBForumTopic"]] = relationship('DBForumTopic', back_populates='icon')
    posts: Mapped[List["DBForumPost"]] = relationship('DBForumPost', back_populates='icon')

    def __init__(
        self,
        name: str,
        location: str
    ) -> None:
        self.name = name
        self.location = location

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

    def __init__(
        self,
        forum_id: int,
        creator_id: int,
        title: str,
        status_text: str | None,
        icon_id: int | None,
        can_star: bool,
        can_change_icon: bool,
        announcement: bool,
        hidden: bool,
        pinned: bool
    ) -> None:
        self.forum_id = forum_id
        self.creator_id = creator_id
        self.title = title
        self.status_text = status_text
        self.icon_id = icon_id
        self.can_star = can_star
        self.can_change_icon = can_change_icon
        self.announcement = announcement
        self.hidden = hidden
        self.pinned = pinned

class DBForumStar(Base):
    __tablename__ = "forum_stars"

    topic_id   = Column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)
    user_id    = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    user: Mapped["DBUser"] = relationship('DBUser', back_populates='starred_topics')
    topic: Mapped["DBForumTopic"] = relationship('DBForumTopic', back_populates='stars')

    def __init__(
        self,
        topic_id: int,
        user_id: int
    ) -> None:
        self.topic_id = topic_id
        self.user_id = user_id
        self.created_at = datetime.now()

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

    def __init__(
        self,
        topic_id: int,
        forum_id: int,
        user_id: int,
        content: str,
        draft: bool,
        edit_locked: bool,
        icon_id: int | None,
        hidden: bool
    ) -> None:
        self.topic_id = topic_id
        self.forum_id = forum_id
        self.user_id = user_id
        self.content = content
        self.draft = draft
        self.edit_locked = edit_locked
        self.created_at = datetime.now()
        self.edit_time = datetime.now()
        self.icon_id = icon_id
        self.hidden = hidden

class DBForumReport(Base):
    __tablename__ = "forum_reports"

    post_id     = Column('post_id', Integer, ForeignKey('forum_posts.id'), primary_key=True)
    user_id     = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    created_at  = Column('created_at', DateTime, server_default=func.now())
    resolved_at = Column('resolved_at', DateTime, nullable=True)
    reason      = Column('reason', String)

    def __init__(
        self,
        post_id: int,
        user_id: int,
        reason: str
    ) -> None:
        self.post_id = post_id
        self.user_id = user_id
        self.reason = reason
        self.created_at = datetime.now()

class DBForumBookmark(Base):
    __tablename__ = "forum_bookmarks"

    user_id  = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    topic_id = Column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='bookmarked_topics')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='bookmarks')

    def __init__(
        self,
        user_id: int,
        topic_id: int
    ) -> None:
        self.user_id = user_id
        self.topic_id = topic_id

class DBForumSubscriber(Base):
    __tablename__ = "forum_subscribers"

    user_id  = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    topic_id = Column('topic_id', Integer, ForeignKey('forum_topics.id'), primary_key=True)

    user: Mapped['DBUser'] = relationship('DBUser', back_populates='subscribed_topics')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic', back_populates='subscribers')

    def __init__(
        self,
        user_id: int,
        topic_id: int
    ) -> None:
        self.user_id = user_id
        self.topic_id = topic_id
