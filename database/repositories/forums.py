
from __future__ import annotations

from app.common.database.objects import DBForum, DBForumPost, DBForumTopic
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def fetch_by_id(forum_id: int, session: Session | None = None) -> DBForum | None:
    return session.query(DBForum) \
        .filter(DBForum.id == forum_id) \
        .first()

@session_wrapper
def fetch_by_name(name: str, session: Session | None = None) -> DBForum | None:
    return session.query(DBForum) \
        .filter(DBForum.name == name) \
        .first()

@session_wrapper
def fetch_all(session: Session | None = None) -> List[DBForum]:
    return session.query(DBForum) \
        .filter(DBForum.hidden == False) \
        .all()

@session_wrapper
def fetch_main_forums(session: Session | None = None) -> List[DBForum]:
    return session.query(DBForum) \
        .filter(DBForum.parent_id == None) \
        .filter(DBForum.hidden == False) \
        .all()

@session_wrapper
def fetch_sub_forums(parent_id: int, session: Session | None = None) -> List[DBForum]:
    return session.query(DBForum) \
        .filter(DBForum.parent_id == parent_id) \
        .filter(DBForum.hidden == False) \
        .all()

@session_wrapper
def fetch_post_count(forum_id: int, session: Session | None = None) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.forum_id == forum_id) \
        .count()

@session_wrapper
def fetch_topic_count(forum_id: int, session: Session | None = None) -> int:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .count()