
from __future__ import annotations

from app.common.database.objects import DBForumPost, DBUser, DBGroupEntry
from .wrapper import session_wrapper

from sqlalchemy.orm import Session, selectinload
from typing import Dict, Iterable, List
from datetime import datetime
from sqlalchemy import func

@session_wrapper
def create(
    topic_id: int,
    forum_id: int,
    user_id: int,
    content: str,
    draft: bool = False,
    edit_locked: bool = False,
    icon_id: int | None = None,
    hidden: bool = False,
    session: Session = ...
) -> DBForumPost:
    post = DBForumPost(
        topic_id=topic_id,
        forum_id=forum_id,
        user_id=user_id,
        content=content,
        draft=draft,
        edit_locked=edit_locked,
        icon_id=icon_id,
        hidden=hidden,
        created_at=datetime.now(),
        edit_time=datetime.now()
    )
    session.add(post)
    session.flush()
    return post

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.id == id) \
        .first()

@session_wrapper
def fetch_all_by_topic(
    topic_id: int,
    session: Session = ...
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
    session: Session = ...
) -> List[DBForumPost]:
    return session.query(DBForumPost) \
        .options(
            selectinload(DBForumPost.user)
            .selectinload(DBUser.groups)
            .selectinload(DBGroupEntry.group)
        ) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.asc()) \
        .limit(range) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_initial_post(topic_id: int, session: Session = ...) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.asc()) \
        .first()

@session_wrapper
def fetch_initial_posts(
    topic_ids: Iterable[int],
    session: Session = ...
) -> Dict[int, DBForumPost]:
    topic_ids = tuple(topic_ids)

    if not topic_ids:
        return {}

    subquery = session.query(
        DBForumPost.topic_id.label('topic_id'),
        func.min(DBForumPost.id).label('min_id')
    ) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBForumPost.topic_id.in_(topic_ids)) \
        .group_by(DBForumPost.topic_id) \
        .subquery()

    rows = session.query(DBForumPost) \
        .join(
            subquery,
            (DBForumPost.topic_id == subquery.c.topic_id) &
            (DBForumPost.id == subquery.c.min_id)
        ) \
        .all()

    return {row.topic_id: row for row in rows}

@session_wrapper
def fetch_initial_post_id(topic_id: int, session: Session = ...) -> DBForumPost | None:
    result = session.query(DBForumPost.id) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.asc()) \
        .first()

    return result.id if result else None

@session_wrapper
def fetch_topic_id(post_id: int, session: Session = ...) -> int | None:
    result = session.query(DBForumPost.topic_id) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBForumPost.id == post_id) \
        .first()

    return result.topic_id if result else None

@session_wrapper
def fetch_last(topic_id: int, session: Session = ...) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .options(
            selectinload(DBForumPost.user)
            .selectinload(DBUser.groups)
            .selectinload(DBGroupEntry.group)
        ) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.desc()) \
        .first()

@session_wrapper
def fetch_last_by_user(
    topic_id: int,
    user_id: int,
    session: Session = ...
) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.user_id == user_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.desc()) \
        .first()

@session_wrapper
def fetch_last_by_forum(
    forum_id: int,
    session: Session = ...
) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .options(
            selectinload(DBForumPost.user)
            .selectinload(DBUser.groups)
            .selectinload(DBGroupEntry.group)
        ) \
        .filter(DBForumPost.forum_id == forum_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.desc()) \
        .first()

@session_wrapper
def fetch_last_bat_post(topic_id: int, session: Session = ...) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .join(DBUser, DBForumPost.user_id == DBUser.id) \
        .join(DBGroupEntry, DBUser.id == DBGroupEntry.user_id) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBGroupEntry.group_id == 3) \
        .order_by(DBForumPost.id.desc()) \
        .first()

@session_wrapper
def fetch_previous(
    post_id: int,
    topic_id: int,
    session: Session = ...
) -> DBForumPost | None:
    return session.query(DBForumPost) \
        .filter(DBForumPost.id < post_id) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .order_by(DBForumPost.id.desc()) \
        .first()

@session_wrapper
def fetch_count(topic_id: int, session: Session = ...) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .count()

@session_wrapper
def fetch_statistics_by_topic_ids(
    topic_ids: Iterable[int],
    session: Session = ...
) -> Dict[int, int]:
    rows = session.query(
        DBForumPost.topic_id,
        func.count(DBForumPost.id)
    ) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBForumPost.topic_id.in_(topic_ids)) \
        .group_by(DBForumPost.topic_id) \
        .all()

    counts = {topic_id: 0 for topic_id in topic_ids}

    for topic_id, count in rows:
        counts[topic_id] = count

    return counts

@session_wrapper
def fetch_count_before_post(
    post_id: int,
    topic_id: int,
    session: Session = ...
) -> int:
    return session.query(DBForumPost) \
        .filter(DBForumPost.id < post_id) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.hidden == False) \
        .count()

@session_wrapper
def fetch_drafts(user_id: int, topic_id: int, session: Session = ...) -> List[DBForumPost]:
    return session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .filter(DBForumPost.user_id == user_id) \
        .filter(DBForumPost.draft == True) \
        .order_by(DBForumPost.id.desc()) \
        .all()

@session_wrapper
def fetch_last_for_topics(
    topic_ids: Iterable[int],
    session: Session = ...
) -> Dict[int, DBForumPost]:
    subquery = session.query(
        DBForumPost.topic_id.label('topic_id'),
        func.max(DBForumPost.id).label('max_id')
    ) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBForumPost.topic_id.in_(topic_ids)) \
        .group_by(DBForumPost.topic_id) \
        .subquery()

    rows = session.query(DBForumPost) \
        .options(
            selectinload(DBForumPost.user)
            .selectinload(DBUser.groups)
            .selectinload(DBGroupEntry.group)
        ) \
        .join(
            subquery,
            (DBForumPost.topic_id == subquery.c.topic_id) &
            (DBForumPost.id == subquery.c.max_id)
        ) \
        .all()

    return {row.topic_id: row for row in rows}

@session_wrapper
def fetch_last_for_forums(
    forum_ids: Iterable[int],
    session: Session = ...
) -> Dict[int, DBForumPost]:
    subquery = session.query(
        DBForumPost.forum_id.label('forum_id'),
        func.max(DBForumPost.id).label('max_id')
    ) \
        .filter(DBForumPost.hidden == False) \
        .filter(DBForumPost.forum_id.in_(forum_ids)) \
        .group_by(DBForumPost.forum_id) \
        .subquery()

    rows = session.query(DBForumPost) \
        .options(
            selectinload(DBForumPost.user)
            .selectinload(DBUser.groups)
            .selectinload(DBGroupEntry.group)
        ) \
        .join(
            subquery,
            (DBForumPost.forum_id == subquery.c.forum_id) &
            (DBForumPost.id == subquery.c.max_id)
        ) \
        .all()

    return {row.forum_id: row for row in rows}

@session_wrapper
def update_by_topic(
    topic_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBForumPost) \
        .filter(DBForumPost.topic_id == topic_id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def update(
    post_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBForumPost) \
        .filter(DBForumPost.id == post_id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def delete(post_id: int, session: Session = ...) -> int:
    rows = session.query(DBForumPost) \
        .filter(DBForumPost.id == post_id) \
        .delete()
    session.flush()
    return rows
