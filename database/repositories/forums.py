
from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Tuple

from .wrapper import session_wrapper
from app.common.database.objects import (
    DBForumTopic,
    DBForumIcon,
    DBForumPost,
    DBForum
)

@session_wrapper
def fetch_by_id(forum_id: int, session: Session = ...) -> DBForum | None:
    return session.query(DBForum) \
        .filter(DBForum.id == forum_id) \
        .first()

@session_wrapper
def fetch_by_name(name: str, session: Session = ...) -> DBForum | None:
    return session.query(DBForum) \
        .filter(DBForum.name == name) \
        .first()

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBForum]:
    return session.query(DBForum) \
        .filter(DBForum.hidden == False) \
        .all()

@session_wrapper
def fetch_main_forums(session: Session = ...) -> List[DBForum]:
    return session.query(DBForum) \
        .filter(DBForum.parent_id == None) \
        .filter(DBForum.hidden == False) \
        .all()

@session_wrapper
def fetch_sub_forums(parent_id: int, session: Session = ...) -> List[DBForum]:
    return session.query(DBForum) \
        .filter(DBForum.parent_id == parent_id) \
        .filter(DBForum.hidden == False) \
        .all()

@session_wrapper
def fetch_post_count(forum_id: int, session: Session = ...) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.forum_id == forum_id) \
        .filter(DBForumPost.hidden == False) \
        .count()

@session_wrapper
def fetch_topic_count(forum_id: int, session: Session = ...) -> int:
    return session.query(DBForumTopic) \
        .filter(DBForumTopic.forum_id == forum_id) \
        .filter(DBForumTopic.hidden == False) \
        .count()

@session_wrapper
def fetch_icons(session: Session = ...) -> List[DBForumIcon]:
    return session.query(DBForumIcon) \
        .order_by(DBForumIcon.order.asc(), DBForumIcon.id.asc()) \
        .all()

@session_wrapper
def fetch_statistics_by_forum_ids(
    forum_ids: List[int],
    session: Session = ...
) -> Dict[int, Tuple[int, int]]:
    if not forum_ids:
        return {}

    topic_rows = session.query(
        DBForumTopic.forum_id,
        func.count(DBForumTopic.id)
    ) \
        .filter(DBForumTopic.hidden == False) \
        .filter(DBForumTopic.forum_id.in_(forum_ids)) \
        .group_by(DBForumTopic.forum_id) \
        .all()

    post_rows = session.query(
        DBForumPost.forum_id,
        func.count(DBForumPost.id)
    ) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBForumPost.forum_id.in_(forum_ids)) \
        .group_by(DBForumPost.forum_id) \
        .all()

    topic_counts = {forum_id: 0 for forum_id in forum_ids}
    post_counts = {forum_id: 0 for forum_id in forum_ids}

    for forum_id, count in topic_rows:
        topic_counts[forum_id] = count

    for forum_id, count in post_rows:
        post_counts[forum_id] = count

    return {
        forum_id: (topic_counts[forum_id], post_counts[forum_id])
        for forum_id in forum_ids
    }
