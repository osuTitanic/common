
from __future__ import annotations

from app.common.database.objects import DBForumPost
from .wrapper import session_wrapper

from sqlalchemy.orm import Session
from typing import List

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.id == id) \
        .first()

@session_wrapper
def fetch_all_by_topic(
    topic_id: int,
    session: Session | None = None
) -> List[DBForumPost]:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.asc()) \
        .all()

@session_wrapper
def fetch_range_by_topic(
    topic_id: int,
    range: int,
    offset: int,
    session: Session | None = None
) -> List[DBForumPost]:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.asc()) \
        .limit(range) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_initial_post(topic_id: int, session: Session | None = None) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.asc()) \
        .first()

@session_wrapper
def fetch_last_post(topic_id: int, session: Session | None = None) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.desc()) \
        .first()
