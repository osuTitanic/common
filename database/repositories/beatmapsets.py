
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

from ...helpers.caching import ttl_cache

from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_, and_

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
    with app.session.database.managed_session() as session:
        return session.query(DBBeatmapset) \
                    .filter(DBBeatmapset.id == id) \
                    .first()

def search(
    query_string: str,
    user_id: int,
    display_mode = DisplayMode.All
) -> List[DBBeatmapset]:
    with app.session.database.managed_session() as session:
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
            conditions = []

            keywords = [
                f'{word}%' for word in query_string.strip() \
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
    conditions = []

    keywords = [
        f'{word}%' for word in query_string.strip() \
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

    with app.session.database.managed_session() as session:
        return session.query(DBBeatmapset) \
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
    order: BeatmapOrder,
    category: BeatmapCategory,
    sort: BeatmapSortBy,
    has_storyboard: bool,
    has_video: bool,
    offset: int = 0,
    limit: int = 50
) -> List[DBBeatmapset]:
    with app.session.database.managed_session() as session:
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
