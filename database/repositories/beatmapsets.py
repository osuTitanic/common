
from app.common.constants import DisplayMode
from app.common.database.objects import (
    DBBeatmapset,
    DBBeatmap,
    DBRating,
    DBPlay
)

from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_

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
                .filter(or_(
                    func.lower(DBBeatmapset.artist).contains(query_string.lower()),
                    func.lower(DBBeatmapset.title).contains(query_string.lower()),
                    func.lower(DBBeatmap.version).contains(query_string.lower()),
                    func.lower(DBBeatmapset.creator).contains(query_string.lower()),
                    func.lower(DBBeatmapset.source).contains(query_string.lower()),
                    func.lower(DBBeatmapset.tags).contains(query_string.lower())
                ))

    return query.limit(100).all()
