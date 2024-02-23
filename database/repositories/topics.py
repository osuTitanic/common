
from __future__ import annotations

from app.common.database.objects import DBForumTopic, DBForumPost
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import List

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> DBForumTopic | None:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.id == id) \
        .first()

@session_wrapper
def fetch_all(session: Session | None = None) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .all()

@session_wrapper
def fetch_by_forum(
    forum_id: int,
    session: Session | None = None
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
    session: Session | None = None
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
    offset: int,
    session: Session | None = None
) -> List[DBForumTopic]:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.announcement == True) \
        .filter(DBForumTopic.hidden == False) \
        .order_by(DBForumTopic.id.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_post_count(topic_id: int, session: Session | None = None) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .count()
