
from __future__ import annotations

from app.common.constants import (
    BeatmapCategory,
    BeatmapSortBy,
    BeatmapOrder,
    DisplayMode
)

from app.common.database.objects import (
    DBBeatmapset,
    DBBeatmap,
    DBRating,
    DBPlay
)

from sqlalchemy.orm import selectinload, Session
from .wrapper import session_wrapper
from sqlalchemy import func, or_

from datetime import datetime
from typing import List

import re

def text_search_condition(query_string: str):
    search_columns = [
        DBBeatmapset.search,
        DBBeatmap.search
    ]

    sanitized_query = re.sub(
        r'[^\w\s]', '',
        query_string
    )

    words = [
        word.strip()
        for word in sanitized_query.split()
    ]

    main_tsquery = func.plainto_tsquery(
        'simple',
        query_string
    )

    fuzzy_tsquery = func.to_tsquery(
        'simple',
        ' & '.join(f'{word}:*' for word in words)
    )

    return or_(
        *[
            column.op('@@')(main_tsquery)
            for column in search_columns
        ],
        *[
            column.op('@@')(fuzzy_tsquery)
            for column in search_columns
        ]
    )

@session_wrapper
def create(
    id: int,
    title: str = '',
    title_unicode: str = '',
    artist: str = '',
    artist_unicode: str = '',
    creator: str = '',
    source: str = '',
    tags: str = '',
    description: str = '',
    status: int = -3,
    has_video: bool = False,
    has_storyboard: bool = False,
    language_id: int = 1,
    genre_id: int = 1,
    osz_filesize: int = 0,
    osz_filesize_novideo: int = 0,
    available: bool = True,
    server: int = 0,
    creator_id: int = None,
    submit_date: datetime | None = None,
    approved_date: datetime | None = None,
    last_update: datetime | None = None,
    display_title: str | None = None,
    session: Session = ...
) -> DBBeatmapset:
    session.add(
        s := DBBeatmapset(
            id=id,
            title=title,
            title_unicode=title_unicode,
            artist=artist,
            artist_unicode=artist_unicode,
            creator=creator,
            source=source,
            tags=tags,
            description=description,
            display_title=display_title or f'[bold:0,size:20]{artist or ""}|[]{title or ""}',
            status=status,
            has_video=has_video,
            has_storyboard=has_storyboard,
            created_at=submit_date or datetime.now(),
            approved_at=approved_date,
            last_update=last_update or datetime.now(),
            language_id=language_id,
            genre_id=genre_id,
            osz_filesize=osz_filesize,
            osz_filesize_novideo=osz_filesize_novideo,
            available=available,
            server=server,
            creator_id=creator_id
        )
    )
    session.commit()
    session.refresh(s)
    return s

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBBeatmapset | None:
    return session.query(DBBeatmapset) \
            .filter(DBBeatmapset.id == id) \
            .first()

@session_wrapper
def fetch_by_creator(
    creator_id: int,
    session: Session = ...
) -> List[DBBeatmapset]:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.creator_id == creator_id) \
        .all()

@session_wrapper
def fetch_by_topic(
    topic_id: int,
    session: Session = ...
) -> DBBeatmapset | None:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.topic_id == topic_id) \
        .first()

@session_wrapper
def fetch_by_status(
    status: int,
    session: Session = ...
) -> DBBeatmapset | None:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.status == status) \
        .all()

@session_wrapper
def search(
    query_string: str,
    user_id: int,
    display_mode = DisplayMode.All,
    offset: int = 0,
    mode: int = -1,
    session: Session = ...
) -> List[DBBeatmapset]:
    query = session.query(DBBeatmapset) \
                   .join(DBBeatmap, isouter=True)

    if mode != -1:
        query = query.filter(DBBeatmap.mode == mode)

    if query_string == 'Newest':
        query = query.order_by(DBBeatmapset.created_at.desc()) \
                     .distinct()

    elif query_string == 'Top Rated':
        query = query.join(DBRating) \
                     .group_by(DBBeatmapset.id) \
                     .order_by(func.avg(DBRating.rating).desc())

    elif query_string == 'Most Played':
        query = query.group_by(DBBeatmapset.id) \
                     .order_by(func.sum(DBBeatmap.playcount).desc())

    else:
        query = query.filter(text_search_condition(query_string))

    query = {
        DisplayMode.All: query.filter(DBBeatmapset.status > -3),
        DisplayMode.Ranked: query.filter(DBBeatmapset.status > 0),
        DisplayMode.Pending: query.filter(DBBeatmapset.status == 0),
        DisplayMode.Graveyard: query.filter(DBBeatmapset.status == -2),
        DisplayMode.Qualified: query.filter(DBBeatmapset.status == 3),
        DisplayMode.Played: query.join(DBPlay) \
            .filter(DBPlay.user_id == user_id) \
            .filter(DBBeatmapset.status > 0)
    }.get(display_mode, query)

    return query.limit(100) \
        .offset(offset) \
        .options(
            selectinload(DBBeatmapset.beatmaps),
            selectinload(DBBeatmapset.ratings)
        ).all()

@session_wrapper
def search_one(
    query_string: str,
    offset: int = 0,
    session: Session = ...
) -> DBBeatmapset | None:
    return session.query(DBBeatmapset) \
        .join(DBBeatmap) \
        .filter(DBBeatmapset.status > -3) \
        .filter(text_search_condition(query_string)) \
        .order_by(DBBeatmap.playcount.desc()) \
        .offset(offset) \
        .first()

@session_wrapper
def search_extended(
    query_string: str | None,
    genre: int | None,
    language: int | None,
    played: bool | None,
    user_id: int | None,
    mode: int | None,
    order: BeatmapOrder,
    category: BeatmapCategory,
    sort: BeatmapSortBy,
    has_storyboard: bool,
    has_video: bool,
    offset: int = 0,
    limit: int = 50,
    session: Session = ...
) -> List[DBBeatmapset]:
    query = session.query(DBBeatmapset) \
            .options(
                selectinload(DBBeatmapset.beatmaps),
                selectinload(DBBeatmapset.ratings),
                selectinload(DBBeatmapset.favourites)
            ) \
            .group_by(DBBeatmapset.id) \
            .join(DBBeatmap)

    if query_string:
        query = query.filter(text_search_condition(query_string))

    if sort == BeatmapSortBy.Rating:
        query = query.join(DBRating)

    order_type = {
        BeatmapSortBy.Created: DBBeatmapset.id,
        BeatmapSortBy.Title: DBBeatmapset.title,
        BeatmapSortBy.Artist: DBBeatmapset.artist,
        BeatmapSortBy.Creator: DBBeatmapset.creator,
        BeatmapSortBy.Ranked: DBBeatmapset.approved_at,
        BeatmapSortBy.Difficulty: func.max(DBBeatmap.diff),
        BeatmapSortBy.Rating: func.avg(DBRating.rating),
        BeatmapSortBy.Plays: func.sum(DBBeatmap.playcount),
    }[sort]

    query = query.order_by(
        order_type.asc() if order == BeatmapOrder.Ascending else
        order_type.desc()
    )

    if genre is not None:
        query = query.filter(DBBeatmapset.genre_id == genre)

    if language is not None:
        query = query.filter(DBBeatmapset.language_id == language)

    if mode is not None:
        query = query.filter(DBBeatmapset.beatmaps.any(DBBeatmap.mode == mode))

    if has_storyboard:
        query = query.filter(DBBeatmapset.has_storyboard == True)

    if has_video:
        query = query.filter(DBBeatmapset.has_video == True)

    if (played is not None and
       user_id is not None):
        query = query.join(DBPlay) \
                     .filter(DBPlay.user_id == user_id)

    query = query.filter({
        BeatmapCategory.Any: (DBBeatmapset.status > -3),
        BeatmapCategory.Leaderboard: (DBBeatmapset.status > 0),
        BeatmapCategory.Pending: (DBBeatmapset.status == 0),
        BeatmapCategory.Ranked: (DBBeatmapset.status == 1),
        BeatmapCategory.Approved: (DBBeatmapset.status == 2),
        BeatmapCategory.Qualified: (DBBeatmapset.status == 3),
        BeatmapCategory.Loved: (DBBeatmapset.status == 4),
    }[category])

    return query.offset(offset) \
                .limit(limit) \
                .all()

@session_wrapper
def fetch_unranked_count(
    user_id: int,
    session: Session = ...
) -> int:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.creator_id == user_id) \
        .filter(DBBeatmapset.status <= 0) \
        .count()

@session_wrapper
def fetch_ranked_count(
    user_id: int,
    session: Session = ...
) -> int:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.creator_id == user_id) \
        .filter(DBBeatmapset.status > 0) \
        .count()

@session_wrapper
def fetch_inactive(
    user_id: int,
    session: Session = ...
) -> List[DBBeatmapset]:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.creator_id == user_id) \
        .filter(DBBeatmapset.status == -3) \
        .all()

@session_wrapper
def update(
    beatmapset_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmapset) \
        .filter(DBBeatmapset.id == beatmapset_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def delete_by_id(
    id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBBeatmapset) \
        .filter(DBBeatmapset.id == id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def delete_inactive(user_id: int, session: Session = ...) -> int:
    rows = session.query(DBBeatmapset) \
        .filter(DBBeatmapset.creator_id == user_id) \
        .filter(DBBeatmapset.status == -3) \
        .delete()
    session.commit()
    return rows
