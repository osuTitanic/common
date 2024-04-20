
from __future__ import annotations

from app.common.database.objects import DBForumTopic, DBForumPost
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import List

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
def fetch_post_count(topic_id: int, session: Session = ...) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .count()

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
