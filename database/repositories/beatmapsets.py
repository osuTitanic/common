
from __future__ import annotations

from app.common.helpers import caching
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
    DBScore,
    DBPlay
)

from sqlalchemy import func, select, or_, ColumnElement
from sqlalchemy.orm import selectinload, Session
from .wrapper import session_wrapper

from datetime import datetime
from typing import List

import app
import re

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
def fetch_count(session: Session = ...) -> int:
    return session.query(func.count(DBBeatmapset.id)) \
                  .scalar()

@session_wrapper
def fetch_by_creator(
    creator_id: int,
    session: Session = ...
) -> List[DBBeatmapset]:
    return session.query(DBBeatmapset) \
        .filter(DBBeatmapset.creator_id == creator_id) \
        .order_by(DBBeatmapset.created_at.desc()) \
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
def search_one(
    query_string: str,
    offset: int = 0,
    session: Session = ...
) -> DBBeatmapset | None:
    condition, sort = text_search_condition(query_string)

    return session.query(DBBeatmapset) \
        .join(DBBeatmap) \
        .filter(DBBeatmapset.status > -3) \
        .filter(condition) \
        .order_by(sort.desc()) \
        .offset(offset) \
        .first()

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
        .join(DBBeatmap, isouter=True) \
        .filter(DBBeatmapset.beatmaps.any()) \
        .group_by(DBBeatmapset.id)

    text_condition, text_sort = text_search_condition(query_string)

    is_approved = display_mode not in (
        DisplayMode.Graveyard,
        DisplayMode.Pending,
        DisplayMode.All
    )

    order_column = (
        DBBeatmapset.approved_at if is_approved else
        DBBeatmapset.last_update
    )

    if mode != -1:
        query = query.filter(DBBeatmap.mode == mode)

    if query_string == 'Newest':
        query = query.order_by(order_column.desc())

    elif query_string == 'Most Played':
        query = query.order_by(DBBeatmapset.total_playcount.desc())

    elif query_string == 'Top Rated':
        query = query.join(DBRating) \
                     .order_by(bayesian_rating().desc())

    elif query_string.isdigit():
        query = query.filter(
            or_(
                DBBeatmapset.id == int(query_string),
                DBBeatmap.id == int(query_string),
                text_condition
            )) \
            .order_by(text_sort.desc())

    else:
        query = query.filter(text_condition) \
                     .order_by(text_sort.desc())

    query = {
        DisplayMode.All: query.filter(DBBeatmapset.status > -3),
        DisplayMode.Ranked: query.filter(DBBeatmapset.status > 0),
        DisplayMode.Pending: query.filter(DBBeatmapset.status == 0),
        DisplayMode.Graveyard: query.filter(DBBeatmapset.status == -2),
        DisplayMode.Qualified: query.filter(DBBeatmapset.status == 3),
        DisplayMode.Loved: query.filter(DBBeatmapset.status == 4),
        DisplayMode.Played: query.join(DBBeatmapset.plays) \
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
def search_extended(
    query_string: str | None = None,
    genre: int | None = None,
    language: int | None = None,
    played: bool | None = None,
    unplayed: bool | None = None,
    cleared: bool | None = None,
    uncleared: bool | None = None,
    user_id: int | None = None,
    mode: int | None = None,
    order: BeatmapOrder = BeatmapOrder.Descending,
    category: BeatmapCategory = BeatmapCategory.Leaderboard,
    sort: BeatmapSortBy = BeatmapSortBy.Relevance,
    has_storyboard: bool = False,
    has_video: bool = False,
    titanic_only: bool = False,
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
            .join(DBBeatmap) \
            .filter(DBBeatmapset.beatmaps.any())

    text_condition, text_sort = None, DBBeatmapset.approved_at

    if query_string:
        text_condition, text_sort = text_search_condition(query_string)
        query = query.filter(text_condition)

    if sort == BeatmapSortBy.Rating:
        query = query.join(DBRating)

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

    if titanic_only:
        query = query.filter(or_(
            DBBeatmapset.server == 1,
            DBBeatmapset.enhanced == True
        ))

    if user_id is not None:
        if played is not None:
            query = query.join(DBPlay) \
                         .filter(DBPlay.user_id == user_id)

        if cleared is not None:
            query = query.join(DBScore, DBScore.beatmap_id == DBBeatmap.id) \
                         .filter(DBScore.user_id == user_id) \
                         .filter(DBScore.status_pp >= 2)

        if unplayed is not None:
            subquery = select(DBPlay.beatmap_id) \
                    .filter(DBPlay.user_id == user_id) \
                    .subquery()

            query = query.filter(DBBeatmap.id.notin_(subquery))

        if uncleared is not None:
            subquery = select(DBScore.beatmap_id) \
                    .filter(DBScore.user_id == user_id) \
                    .subquery()

            query = query.filter(DBBeatmap.id.notin_(subquery))

    order_type = {
        BeatmapSortBy.Created: DBBeatmapset.id,
        BeatmapSortBy.Title: DBBeatmapset.title,
        BeatmapSortBy.Artist: DBBeatmapset.artist,
        BeatmapSortBy.Creator: DBBeatmapset.creator,
        BeatmapSortBy.Ranked: DBBeatmapset.approved_at,
        BeatmapSortBy.Plays: DBBeatmapset.total_playcount,
        BeatmapSortBy.Difficulty: func.max(DBBeatmap.diff),
        BeatmapSortBy.Rating: bayesian_rating(),
        BeatmapSortBy.Relevance: text_sort
    }[sort]

    query = query.order_by(
        order_type.asc() if order == BeatmapOrder.Ascending else
        order_type.desc()
    )

    query = query.filter({
        BeatmapCategory.Any: (DBBeatmapset.status > -3),
        BeatmapCategory.Leaderboard: (DBBeatmapset.status > 0),
        BeatmapCategory.Graveyard: (DBBeatmapset.status == -2),
        BeatmapCategory.WIP: (DBBeatmapset.status == -1),
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
def fetch_most_played(
    limit: int = 5,
    offset: int = 0,
    session: Session = ...
) -> List[dict]:
    results = session.query(DBBeatmapset) \
        .order_by(DBBeatmapset.total_playcount.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

    return [
        {
            "beatmapset": beatmapset,
            "playcount": beatmapset.total_playcount
        }
        for beatmapset in results
    ]

@session_wrapper
def fetch_server_id(
    beatmapset_id: int,
    session: Session = ...
) -> int:
    return session.query(DBBeatmapset.server) \
        .filter(DBBeatmapset.id == beatmapset_id) \
        .scalar() or 0

@session_wrapper
def fetch_download_server_id(
    beatmapset_id: int,
    session: Session = ...
) -> int:
    return session.query(DBBeatmapset.download_server) \
        .filter(DBBeatmapset.id == beatmapset_id) \
        .scalar() or 0

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

@caching.ttl_cache(ttl=60*60*12)
def global_average_rating() -> int:
    with app.session.database.managed_session() as session:
        result = session.query(func.avg(DBRating.rating)).scalar()
        return result or 0

def bayesian_rating() -> ColumnElement:
    # Use bayesian average to calculate rating
    # https://en.wikipedia.org/wiki/Bayesian_average
    confidence_factor = 25
    rating_sum = func.avg(DBRating.rating) * func.count(DBRating.rating)
    total_count = func.count(DBRating.rating) + confidence_factor
    adjusted_avg_rating = global_average_rating() * confidence_factor
    return (rating_sum + adjusted_avg_rating) / total_count

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

    rank = func.ts_rank(
        DBBeatmapset.search,
        main_tsquery
    )

    query = or_(
        *[
            column.op('@@')(main_tsquery)
            for column in search_columns
        ],
        *[
            column.op('@@')(fuzzy_tsquery)
            for column in search_columns
        ]
    )

    return query, rank
