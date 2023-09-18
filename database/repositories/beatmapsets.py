
from app.common.constants import DisplayMode
from app.common.database.objects import (
    DBBeatmapset,
    DBBeatmap,
    DBRating,
    DBPlay
)

from sqlalchemy.orm import selectinload
from sqlalchemy import func

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
    query = app.session.database.session.query(DBBeatmapset) \
               .options(
                   selectinload(DBBeatmapset.beatmaps),
                   selectinload(DBBeatmapset.ratings)
               )

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
        query = query.join(DBBeatmap) \
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
                     .order_by(DBBeatmap.playcount.desc())

    return query.limit(100).all()

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
