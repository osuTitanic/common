
from app.common.constants import DisplayMode, BeatmapSortBy
from app.common.database.objects import (
    DBBeatmapset,
    DBBeatmap,
    DBRating,
    DBPlay
)

from sqlalchemy import func, or_, and_, desc
from sqlalchemy.orm import selectinload

from typing import Optional, List
from datetime import datetime

import app

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
    server: int = 0
) -> DBBeatmapset:
    with app.session.database.managed_session() as session:
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

def fetch_one(id: int) -> Optional[DBBeatmapset]:
    return app.session.database.session.query(DBBeatmapset) \
                .filter(DBBeatmapset.id == id) \
                .first()

def search(
    query_string: str,
    user_id: int,
    display_mode = DisplayMode.All
) -> List[DBBeatmapset]:
    session = app.session.database.session
    query = session.query(DBBeatmapset)

    if query_string == 'Newest':
        query = query.order_by(DBBeatmapset.created_at.desc())

    elif query_string == 'Top Rated':
        query = query.join(DBRating) \
                     .group_by(DBBeatmapset.id) \
                     .order_by(func.avg(DBRating.rating).desc())

    elif query_string == 'Most Played':
        query = query.join(DBBeatmap) \
                     .group_by(DBBeatmapset.id) \
                     .order_by(func.sum(DBBeatmap.playcount).desc())

    else:
        stop_words = ['the', 'and', 'of', 'in', 'to', 'for']
        conditions = []

        keywords = [
            f'{word}%' for word in query_string.strip() \
                .replace(' - ', ' ') \
                .lower() \
                .split()
            if word not in stop_words
        ]

        searchable_columns = [
            func.to_tsvector('english', column)
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
                    col.op('@@')(func.plainto_tsquery('english', word))
                    for col in searchable_columns
                ]
            ))

        query = query.join(DBBeatmap) \
                .filter(and_(*conditions)) \
                .order_by(DBBeatmap.playcount.desc())

    if display_mode == DisplayMode.Ranked:
        query = query.filter(DBBeatmapset.status > 0)

    elif display_mode == DisplayMode.Pending:
        query = query.filter(DBBeatmapset.status == 0)

    elif display_mode == DisplayMode.Graveyard:
        query = query.filter(DBBeatmapset.status == -1)

    elif display_mode == DisplayMode.Played:
        query = query.join(DBPlay) \
                     .filter(DBPlay.user_id == user_id) \
                     .filter(DBBeatmapset.status > 0)

    return query.limit(100) \
                .options(
                        selectinload(DBBeatmapset.beatmaps),
                        selectinload(DBBeatmapset.ratings)
                ) \
                .all()

def search_one(query_string: str, offset: int = 0) -> Optional[DBBeatmapset]:
    stop_words = ['the', 'and', 'of', 'in', 'to', 'for']
    conditions = []

    keywords = [
        f'{word}%' for word in query_string.strip() \
            .replace(' - ', ' ') \
            .lower() \
            .split()
        if word not in stop_words
    ]

    searchable_columns = [
        func.to_tsvector('english', column)
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
                col.op('@@')(func.plainto_tsquery('english', word))
                for col in searchable_columns
            ]
        ))

    return app.session.database.session.query(DBBeatmapset) \
            .join(DBBeatmap) \
            .filter(and_(*conditions)) \
            .order_by(DBBeatmap.playcount.desc()) \
            .first()

def search_extended(
    query_string: Optional[str],
    genre: Optional[int],
    language: Optional[int],
    played: Optional[bool],
    user_id: Optional[int],
    mode: Optional[int],
    status: Optional[int],
    sort: BeatmapSortBy,
    has_storyboard: bool,
    has_video: bool,
    offset: int = 0,
    limit: int = 50
) -> List[DBBeatmapset]:
    conditions = []

    if query_string:
        stop_words = ['the', 'and', 'of', 'in', 'to', 'for']
        conditions = []

        keywords = [
            f'%{word}%' for word in query_string.strip() \
                .replace(' - ', ' ') \
                .lower() \
                .split()
            if word not in stop_words
        ]

        searchable_columns = [
            func.to_tsvector('english', column)
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
                    col.op('@@')(func.plainto_tsquery('english', word))
                    for col in searchable_columns
                ]
            ))

    query = app.session.database.session.query(DBBeatmapset) \
            .options(selectinload(DBBeatmapset.beatmaps)) \
            .join(DBBeatmap) \
            .join(DBRating) \
            .filter(and_(*conditions)) \
            .group_by(DBBeatmapset.id) \
            .order_by({
                BeatmapSortBy.Title: DBBeatmapset.title.asc(),
                BeatmapSortBy.Artist: DBBeatmapset.artist.asc(),
                BeatmapSortBy.Creator: DBBeatmapset.creator.asc(),
                BeatmapSortBy.RankedAsc: DBBeatmapset.approved_at.asc(),
                BeatmapSortBy.RankedDesc: DBBeatmapset.approved_at.desc(),
                BeatmapSortBy.Difficulty: func.max(DBBeatmap.diff).desc(),
                BeatmapSortBy.Rating: func.avg(DBRating.rating).desc(),
                BeatmapSortBy.Plays: func.sum(DBBeatmap.playcount).desc(),
            }[sort])
    
    if genre is not None:
        query = query.filter(DBBeatmapset.genre_id == genre)

    if language is not None:
        query = query.filter(DBBeatmapset.language_id == language)

    if status is not None:
        query = query.filter(DBBeatmapset.status == status)

    if has_storyboard:
        query = query.filter(DBBeatmapset.has_storyboard == True)

    if has_video:
        query = query.filter(DBBeatmapset.has_video == True)

    if mode is not None:
        query = query.filter(
            DBBeatmapset.beatmaps.any(DBBeatmap.mode == mode)
        )

    if (played is not None and
       user_id is not None):
        query = query.join(DBPlay) \
                     .filter(DBPlay.user_id == user_id)

    return query.offset(offset) \
                .limit(limit) \
                .all()
