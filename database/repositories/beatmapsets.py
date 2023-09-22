
from app.common.constants import DisplayMode
from app.common.database.objects import (
    DBBeatmapset,
    DBBeatmap,
    DBRating,
    DBPlay
)

from sqlalchemy import func, or_, and_, desc
from sqlalchemy.orm import selectinload

from typing import Optional, List

import app

# TODO: create

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
            f'{word}%' for word in query_string \
                .replace(' - ', ' ') \
                .lower() \
                .strip() \
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
    query_string = query_string.strip().lower()

    return app.session.database.session.query(DBBeatmapset) \
            .join(DBBeatmap) \
            .filter(
                func.to_tsvector('english', func.lower(DBBeatmapset.title)) \
                    .op('@@')(func.plainto_tsquery('english', query_string)) |
                func.to_tsvector('english', func.lower(DBBeatmapset.artist)) \
                    .op('@@')(func.plainto_tsquery('english', query_string)) |
                func.to_tsvector('english', func.lower(DBBeatmapset.creator)) \
                    .op('@@')(func.plainto_tsquery('english', query_string)) |
                func.to_tsvector('english', func.lower(DBBeatmap.version)) \
                    .op('@@')(func.plainto_tsquery('english', query_string)) |
                func.to_tsvector('english', func.lower(DBBeatmapset.source)) \
                    .op('@@')(func.plainto_tsquery('english', query_string)) |
                func.to_tsvector('english', func.lower(DBBeatmapset.tags)) \
                    .op('@@')(func.plainto_tsquery('english', query_string))
            ) \
            .order_by(DBBeatmap.playcount.desc()) \
            .offset(offset) \
            .first()
