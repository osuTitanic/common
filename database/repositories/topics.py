
from __future__ import annotations

from ..objects import DBForumTopic, DBForumSubscriber, DBForumBookmark
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

@session_wrapper
def create(
    forum_id: int,
    creator_id: int,
    title: str,
    status_text: str | None = None,
    icon_id: int | None = None,
    can_star: bool = False,
    can_change_icon: bool = False,
    announcement: bool = False,
    hidden: bool = False,
    pinned: bool = False,
    session: Session = ...
) -> DBForumTopic:
    topic = DBForumTopic(
        forum_id=forum_id,
        creator_id=creator_id,
        title=title,
        status_text=status_text,
        icon_id=icon_id,
        can_star=can_star,
        can_change_icon=can_change_icon,
        announcement=announcement,
        hidden=hidden,
        pinned=pinned
    )
    session.add(topic)
    session.commit()
    return topic

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBForumTopic | None:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.id == id) \
        .first()

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .all()

@session_wrapper
def fetch_by_forum(
    forum_id: int,
    session: Session = ...
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .all()

@session_wrapper
def fetch_range(
    limit: int,
    offset: int,
    session: Session = ...
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_announcements(
    limit: int,
    offset: int = 0,
    session: Session = ...
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.announcement == True) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_pinned_by_forum_id(
    forum_id: int,
    session: Session = ...
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .filter(DBForumTopic.pinned == True) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .all()

@session_wrapper
def fetch_announcements_by_forum_id(
    forum_id: int,
    limit: int,
    offset: int = 0,
    session: Session = ...
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .filter(DBForumTopic.announcement == True) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_recent(
    forum_id: int,
    session: Session = ...
) -> DBForumTopic | None:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .first()

@session_wrapper
def fetch_recent_many(
    forum_id: int,
    limit: int = 5,
    offset: int = 0,
    session: Session = ...
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def add_subscriber(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> DBForumSubscriber:
    if subscriber := fetch_subscriber(topic_id, user_id, session=session):
        # User already subscribed to this topic
        return subscriber

    subscriber = DBForumSubscriber(
        topic_id=topic_id,
        user_id=user_id
    )
    session.add(subscriber)
    session.commit()
    return subscriber

@session_wrapper
def delete_subscriber(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBForumSubscriber) \
        .filter(DBForumSubscriber.topic_id == topic_id) \
        .filter(DBForumSubscriber.user_id == user_id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def fetch_subscriber(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> DBForumSubscriber | None:
    return session.query(DBForumSubscriber) \
        .filter(DBForumSubscriber.topic_id == topic_id) \
        .filter(DBForumSubscriber.user_id == user_id) \
        .first()

@session_wrapper
def fetch_subscribers(
    topic_id: int,
    session: Session = ...
) -> List[DBForumSubscriber]:
    return session.query(DBForumSubscriber) \
        .filter(DBForumSubscriber.topic_id == topic_id) \
        .all()

def is_subscribed(
    topic_id: int,
    user_id: int,
    session: Session
) -> bool:
    return fetch_subscriber(
        topic_id,
        user_id,
        session=session
    ) is not None

@session_wrapper
def add_bookmark(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> DBForumBookmark:
    if bookmark := fetch_bookmark(topic_id, user_id, session=session):
        # User already subscribed to this topic
        return bookmark

    bookmark = DBForumBookmark(
        topic_id=topic_id,
        user_id=user_id
    )
    session.add(bookmark)
    session.commit()
    return bookmark

@session_wrapper
def delete_bookmark(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBForumBookmark) \
        .filter(DBForumBookmark.topic_id == topic_id) \
        .filter(DBForumBookmark.user_id == user_id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def fetch_bookmark(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> DBForumBookmark | None:
    return session.query(DBForumBookmark) \
        .filter(DBForumBookmark.topic_id == topic_id) \
        .filter(DBForumBookmark.user_id == user_id) \
        .first()

@session_wrapper
def fetch_bookmarks(
    topic_id: int,
    session: Session = ...
) -> List[DBForumBookmark]:
    return session.query(DBForumBookmark) \
        .filter(DBForumBookmark.topic_id == topic_id) \
        .all()

@session_wrapper
def fetch_user_bookmarks(
    user_id: int,
    session: Session = ...
) -> List[DBForumBookmark]:
    return session.query(DBForumBookmark) \
        .filter(DBForumBookmark.user_id == user_id) \
        .all()

@session_wrapper
def is_bookmarked(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> bool:
    return fetch_bookmark(
        topic_id,
        user_id,
        session=session
    ) is not None

@session_wrapper
def fetch_average_views(session: Session = ...) -> float:
    return session.query(func.avg(DBForumTopic.views)) \
                  .scalar()

@session_wrapper
def update(
    id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBForumTopic) \
        .filter(DBForumTopic.id == id) \
        .update(updates)
    session.commit()
    return rows
