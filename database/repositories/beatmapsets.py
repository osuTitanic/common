
from __future__ import annotations

from app.common.helpers import caching
from app.common.constants import (
    FILTER_PATTERN,
    BeatmapCategory,
    DatabaseStatus,
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

from sqlalchemy import func, select, or_, extract, ColumnElement
from sqlalchemy.orm import selectinload, Session, Query
from .wrapper import session_wrapper

from typing import List, Tuple, Dict, Any
from collections import defaultdict
from datetime import datetime

import app
import re

@session_wrapper
def create(
    id: int,
    title: str = "",
    title_unicode: str = "",
    artist: str = "",
    artist_unicode: str = "",
    creator: str = "",
    source: str = "",
    tags: str = "",
    description: str = "",
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
    query = session.query(DBBeatmapset).filter(DBBeatmapset.beatmaps.any())
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

    join_beatmaps = any([
        mode != -1,
        display_mode == DisplayMode.Played,
        query_string not in ('Newest', 'Most Played', 'Top Rated')
    ])

    if join_beatmaps:
        query = query.join(DBBeatmap, DBBeatmapset.beatmaps) \
                     .group_by(DBBeatmapset.id)

    if mode != -1:
        query = query.filter(DBBeatmap.mode == mode)

    if query_string == 'Newest':
        # Sort by either approved date or last update date
        query = query.order_by(order_column.desc())

    elif query_string == 'Most Played':
        # Sort by total playcount
        query = query.order_by(DBBeatmapset.total_playcount.desc())

    elif query_string == 'Top Rated':
        # Use bayesian rating to sort top rated beatmapsets
        query = query.join(DBRating) \
            .order_by(bayesian_rating().desc()) \
            .group_by(DBBeatmapset.id)

    elif query_string.isdigit():
        # Allow for searching beatmap(set)s by IDs
        query = query.filter(
            or_(
                DBBeatmapset.id == int(query_string),
                DBBeatmap.id == int(query_string),
                text_condition
            )) \
            .order_by(text_sort.desc())

    else:
        # Regular full-text search
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
            .filter(DBBeatmapset.beatmaps.any())

    text_condition, text_sort = None, DBBeatmapset.approved_at
    join_ratings = sort == BeatmapSortBy.Rating
    join_beatmaps = any([
        query_string,
        unplayed is not None,
        cleared is not None,
        uncleared is not None,
        mode is not None
    ])

    if query_string:
        # Apply filters, such as year>=2015
        query_string, filters = resolve_search_filters(query_string)
        query = apply_search_filters(query, filters)

        if any(filter in filters for filter in filters_with_beatmaps):
            # Filter requires `DBBeatmap` to be joined
            join_beatmaps = True

    if join_ratings:
        query = query.join(DBRating, DBBeatmapset.ratings) \
                     .group_by(DBBeatmapset.id)

    if join_beatmaps:
        query = query.join(DBBeatmap, DBBeatmapset.beatmaps) \
                     .group_by(DBBeatmapset.id)

    if query_string:
        text_condition, text_sort = text_search_condition(query_string)
        query = query.filter(text_condition)

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

    query = query.filter({
        BeatmapCategory.Any: (DBBeatmapset.status != -3),
        BeatmapCategory.Leaderboard: (DBBeatmapset.status > 0),
        BeatmapCategory.Graveyard: (DBBeatmapset.status == -2),
        BeatmapCategory.WIP: (DBBeatmapset.status == -1),
        BeatmapCategory.Pending: (DBBeatmapset.status == 0),
        BeatmapCategory.Ranked: (DBBeatmapset.status == 1),
        BeatmapCategory.Approved: (DBBeatmapset.status == 2),
        BeatmapCategory.Qualified: (DBBeatmapset.status == 3),
        BeatmapCategory.Loved: (DBBeatmapset.status == 4),
    }[category])

    order_type = {
        BeatmapSortBy.Created: DBBeatmapset.id,
        BeatmapSortBy.Title: DBBeatmapset.title,
        BeatmapSortBy.Artist: DBBeatmapset.artist,
        BeatmapSortBy.Creator: DBBeatmapset.creator,
        BeatmapSortBy.Ranked: DBBeatmapset.approved_at,
        BeatmapSortBy.Difficulty: DBBeatmapset.max_diff,
        BeatmapSortBy.Plays: DBBeatmapset.total_playcount,
        BeatmapSortBy.Rating: bayesian_rating(),
        BeatmapSortBy.Relevance: text_sort
    }[sort]

    query = query.order_by(
        order_type.asc() if order == BeatmapOrder.Ascending else
        order_type.desc()
    )

    return query.offset(offset) \
                .limit(limit) \
                .all()

@caching.ttl_cache(ttl=60*60*12)
def global_average_rating() -> int:
    with app.session.database.managed_session() as session:
        result = session.query(func.avg(DBRating.rating)).scalar()
        return result or 0

def bayesian_rating() -> ColumnElement:
    # Use bayesian average to calculate rating
    # https://en.wikipedia.org/wiki/Bayesian_average
    confidence_factor = 10
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

def resolve_search_filters(query_string: str) -> Tuple[str, Dict[str, Any]]:
    if not query_string:
        return '', {}

    filters = defaultdict(list)
    cleaned_query = query_string

    matches = FILTER_PATTERN.finditer(query_string)

    for match in matches:
        field = match.group(1).lower()
        operator = match.group(2)

        # Value is either the quoted or unquoted part
        value = match.group(3) if match.group(3) else match.group(4)

        # Store the filter
        filters[field].append({
            'operator': operator,
            'value': value
        })

        # Remove this filter from the query string
        cleaned_query = cleaned_query.replace(match.group(0), '', 1)

    return ' '.join(cleaned_query.split()).strip(), filters

def apply_search_filters(query: Query, filters: Dict[str, Any]) -> Query:
    for field, conditions in filters.items():
        if field not in filter_mapping:
            continue

        for condition in conditions:
            query = filter_mapping[field](query, condition)

    return query

def apply_artist_filter(query: Query, condition: Dict[str, Any]) -> Query:
    op = condition['operator']
    val = condition['value']

    if op != '=':
        return query

    artist_filter = or_(
        DBBeatmapset.artist.ilike(f'%{val}%'),
        DBBeatmapset.artist_unicode.ilike(f'%{val}%')
    )
    query = query.filter(artist_filter)
    return query

def apply_title_filter(query: Query, condition: Dict[str, Any]) -> Query:
    op = condition['operator']
    val = condition['value']

    if op != '=':
        return query

    title_filter = or_(
        DBBeatmapset.title.ilike(f'%{val}%'),
        DBBeatmapset.title_unicode.ilike(f'%{val}%')
    )
    query = query.filter(title_filter)
    return query

def apply_creator_filter(query: Query, condition: Dict[str, Any]) -> Query:
    op = condition['operator']
    val = condition['value']

    if op != '=':
        return query

    creator_filter = DBBeatmapset.creator.ilike(f'%{val}%')
    query = query.filter(creator_filter)
    return query

def apply_source_filter(query: Query, condition: Dict[str, Any]) -> Query:
    op = condition['operator']
    val = condition['value']

    if op != '=':
        return query

    source_filter = or_(
        DBBeatmapset.source.ilike(f'%{val}%'),
        DBBeatmapset.source_unicode.ilike(f'%{val}%')
    )
    query = query.filter(source_filter)
    return query

def apply_status_filter(query: Query, condition: Dict[str, Any]) -> Query:
    op = condition['operator']
    val = condition['value']

    status_value = DatabaseStatus.from_lowercase(val.lower())

    if status_value is None:
        if not status_value.isdigit():
            return query

        # Try to use integer value if not matched
        status_value = int(val)

    status_filter = apply_operator(status_value, op, DBBeatmapset.status)
    query = query.filter(status_filter)

    return query

def apply_year_filter(query: Query, condition: Dict[str, Any]):
    if not condition['value'].isdigit():
        return query

    op = condition['operator']
    val = int(condition['value'])

    # Use extract to get year from approved_at
    year_expr = extract('year', DBBeatmapset.approved_at)
    year_filter = apply_operator(val, op, year_expr)

    return query.filter(year_filter)

def apply_created_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query

    op = condition['operator']
    val = int(condition['value'])

    # Use extract to get year from created_at
    year_expr = extract('year', DBBeatmapset.created_at)
    year_filter = apply_operator(val, op, year_expr)

    return query.filter(year_filter)

def apply_difficulty_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not is_float(condition['value']):
        return query

    op = condition['operator']
    val = float(condition['value'])

    diff_filter = apply_operator(val, op, DBBeatmap.diff)
    return query.filter(diff_filter)

def apply_length_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query

    op = condition['operator']
    val = int(condition['value'])

    length_filter = apply_operator(val, op, DBBeatmap.total_length)
    return query.filter(length_filter)

def apply_drain_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query

    op = condition['operator']
    val = int(condition['value'])

    drain_filter = apply_operator(val, op, DBBeatmap.drain_length)
    return query.filter(drain_filter)

def apply_bpm_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not is_float(condition['value']):
        return query

    op = condition['operator']
    val = float(condition['value'])

    bpm_filter = apply_operator(val, op, DBBeatmap.bpm)
    return query.filter(bpm_filter)

def apply_ar_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query
    
    op = condition['operator']
    val = int(condition['value'])

    ar_filter = apply_operator(val, op, DBBeatmap.ar)
    return query.filter(ar_filter)

def apply_cs_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query
    
    op = condition['operator']
    val = int(condition['value'])

    cs_filter = apply_operator(val, op, DBBeatmap.cs)
    return query.filter(cs_filter)

def apply_od_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query
    
    op = condition['operator']
    val = int(condition['value'])

    od_filter = apply_operator(val, op, DBBeatmap.od)
    return query.filter(od_filter)

def apply_hp_filter(query: Query, condition: Dict[str, Any]) -> Query:
    if not condition['value'].isdigit():
        return query
    
    op = condition['operator']
    val = int(condition['value'])

    hp_filter = apply_operator(val, op, DBBeatmap.hp)
    return query.filter(hp_filter)

def apply_operator(value: Any, operator: str, column: ColumnElement) -> ColumnElement:
    assert operator in operator_mapping, f"Unsupported operator: {operator}"
    return operator_mapping[operator](column, value)

def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False

operator_mapping = {
    '=': lambda col, val: col == val,
    '!=': lambda col, val: col != val,
    '>': lambda col, val: col > val,
    '<': lambda col, val: col < val,
    '>=': lambda col, val: col >= val,
    '<=': lambda col, val: col <= val,
}

filter_mapping = {
    'creator': apply_creator_filter,
    'artist': apply_artist_filter,
    'title': apply_title_filter,
    'source': apply_source_filter,
    'status': apply_status_filter,
    'created': apply_created_filter,
    'ranked': apply_year_filter,
    'year': apply_year_filter,
    'difficulty': apply_difficulty_filter,
    'diff': apply_difficulty_filter,
    'stars': apply_difficulty_filter,
    'sr': apply_difficulty_filter,
    'length': apply_length_filter,
    'drain': apply_drain_filter,
    'bpm': apply_bpm_filter,
    'ar': apply_ar_filter,
    'cs': apply_cs_filter,
    'od': apply_od_filter,
    'hp': apply_hp_filter
}

filters_with_beatmaps = (
    'difficulty',
    'length',
    'drain',
    'bpm',
    'ar',
    'cs',
    'od',
    'hp'
)
