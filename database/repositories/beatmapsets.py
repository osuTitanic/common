
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
from sqlalchemy import func, or_, and_
from .wrapper import session_wrapper

from datetime import datetime
from typing import List

@session_wrapper
def create(
    id: int,
    title: str,
    artist: str,
    creator: str,
    source: str,
    tags: str,
    status: int,
    has_video: bool,
    has_storyboard: bool,
    created_at: datetime,
    approved_at: datetime,
    last_update: datetime,
    language_id: int,
    genre_id: int,
    osz_filesize: int = 0,
    osz_filesize_novideo: int = 0,
    available: bool = True,
    server: int = 0,
    session: Session | None = None
) -> DBBeatmapset:
    session.add(
        s := DBBeatmapset(
            id,
            title,
            artist,
            creator,
            source,
            tags,
            status,
            has_video,
            has_storyboard,
            created_at,
            approved_at,
            last_update,
            language_id,
            genre_id,
            osz_filesize,
            osz_filesize_novideo,
            available,
            server
        )
    )
    session.commit()
    session.refresh(s)
    return s

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> DBBeatmapset | None:
    return session.query(DBBeatmapset) \
            .filter(DBBeatmapset.id == id) \
            .first()

@session_wrapper
def search(
    query_string: str,
    user_id: int,
    display_mode = DisplayMode.All,
    offset: int = 0,
    mode: int = -1,
    session: Session | None = None
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
        conditions = []

        keywords = [
            f'%{word}%' for word in query_string.strip() \
                .replace(' - ', ' ') \
                .lower() \
                .split()
        ]

        searchable_columns = [
            func.to_tsvector('simple', column)
            for column in [
                func.lower(DBBeatmapset.title),
                func.lower(DBBeatmapset.artist),
                func.lower(DBBeatmapset.creator),
                func.lower(DBBeatmapset.source),
                func.lower(DBBeatmapset.tags),
                func.lower(DBBeatmap.version)
            ]
        ]

        for word in keywords:
            conditions.append(or_(
                *[
                    col.op('@@')(func.plainto_tsquery('simple', word))
                    for col in searchable_columns
                ]
            ))

        query = query.filter(and_(*conditions)) \
                     .group_by(DBBeatmapset.id) \
                     .order_by(func.sum(DBBeatmap.playcount).desc())

    if display_mode == DisplayMode.Ranked:
        query = query.filter(DBBeatmapset.status > 0)

    elif display_mode == DisplayMode.Pending:
        query = query.filter(DBBeatmapset.status == 0)

    elif display_mode == DisplayMode.Graveyard:
        query = query.filter(DBBeatmapset.status == -1)

    elif display_mode == DisplayMode.Qualified:
        query = query.filter(DBBeatmapset.status == 3)

    elif display_mode == DisplayMode.Played:
        query = query.join(DBPlay) \
                     .filter(DBPlay.user_id == user_id) \
                     .filter(DBBeatmapset.status > 0)

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
    session: Session | None = None
) -> DBBeatmapset | None:
    conditions = []

    keywords = [
        f'%{word}%' for word in query_string.strip() \
            .replace(' - ', ' ') \
            .lower() \
            .split()
    ]

    searchable_columns = [
        func.to_tsvector('simple', column)
        for column in [
            func.lower(DBBeatmapset.title),
            func.lower(DBBeatmapset.artist),
            func.lower(DBBeatmapset.creator),
            func.lower(DBBeatmapset.source),
            func.lower(DBBeatmapset.tags),
            func.lower(DBBeatmap.version)
        ]
    ]

    for word in keywords:
        conditions.append(or_(
            *[
                col.op('@@')(func.plainto_tsquery('simple', word))
                for col in searchable_columns
            ]
        ))

    return session.query(DBBeatmapset) \
        .join(DBBeatmap) \
        .filter(and_(*conditions)) \
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
    session: Session | None = None
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
        conditions = []

        keywords = [
            f'%{word}%' for word in query_string.strip() \
                .replace(' - ', ' ') \
                .lower() \
                .split()
        ]

        searchable_columns = [
            func.to_tsvector('simple', column)
            for column in [
                func.lower(DBBeatmapset.title),
                func.lower(DBBeatmapset.artist),
                func.lower(DBBeatmapset.creator),
                func.lower(DBBeatmapset.source),
                func.lower(DBBeatmapset.tags),
                func.lower(DBBeatmap.version)
            ]
        ]

        for word in keywords:
            conditions.append(or_(
                *[
                    col.op('@@')(func.plainto_tsquery('simple', word))
                    for col in searchable_columns
                ]
            ))

        query = query.filter(and_(*conditions))

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

    if category > BeatmapCategory.Any:
        query = query.filter({
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
def update(
    beatmapset_id: int,
    updates: dict,
    session: Session | None = None
) -> int:
    rows = session.query(DBBeatmapset) \
        .filter(DBBeatmapset.id == beatmapset_id) \
        .update(updates)
    session.commit()
    return rows
