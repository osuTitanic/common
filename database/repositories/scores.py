
from __future__ import annotations

from app.common.constants import Grade
from app.common.database.objects import (
    DBBeatmap,
    DBScore,
    DBUser
)

from sqlalchemy.orm import selectinload, Session
from sqlalchemy import or_, and_, func
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

from .wrapper import session_wrapper

import app

@session_wrapper
def create(score: DBScore, session: Session = ...) -> DBScore:
    session.add(score)
    session.commit()
    session.refresh(score)
    return score

@session_wrapper
def update(
    score_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBScore) \
        .filter(DBScore.id == score_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def update_by_beatmap_id(
    beatmap_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBScore) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .update(updates)
    session.commit()
    return rows

@session_wrapper
def hide_all(user_id: int, session: Session = ...) -> int:
    rows = session.query(DBScore) \
            .filter(DBScore.user_id == user_id) \
            .update({
                'status': -1
            })
    session.commit()
    return rows

@session_wrapper
def fetch_by_id(id: int, session: Session = ...) -> DBScore | None:
    return session.query(DBScore) \
        .options(
            selectinload(DBScore.beatmap),
            selectinload(DBScore.user)
        ) \
        .filter(DBScore.id == id) \
        .first()

@session_wrapper
def fetch_by_replay_checksum(checksum: str, session: Session = ...) -> DBScore | None:
    return session.query(DBScore) \
        .filter(DBScore.replay_md5 == checksum) \
        .first()

@session_wrapper
def fetch_count(user_id: int, mode: int, session: Session = ...) -> int:
    return session.query(func.count(DBScore.id)) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .scalar()

@session_wrapper
def fetch_total_count(session: Session = ...) -> int:
    return session.query(func.count(DBScore.id)) \
        .filter(DBScore.status != -1) \
        .scalar()

@session_wrapper
def fetch_count_beatmap(
    beatmap_id: int,
    mode: int,
    mods: int | None = None,
    country: str | None = None,
    friends: List[int | None] = None,
    session: Session = ...
) -> int:
    query = session.query(func.count(DBScore.id)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode)

    if country is not None:
        query = query.filter(DBUser.country == country) \
                     .join(DBScore.user)

    if friends is not None:
        query = query.filter(DBScore.user_id.in_(friends))

    if mods is not None:
        query = query.filter(or_(DBScore.status == 3, DBScore.status == 4)) \
                     .filter(DBScore.mods == mods)
    else:
        query = query.filter(DBScore.status == 3)

    return query.scalar()

@session_wrapper
def fetch_top_scores(
    user_id: int,
    mode: int,
    exclude_approved: bool = False,
    limit: int = 100,
    offset: int = 0,
    session: Session = ...
) -> List[DBScore]:
    allowed_status = [
        1, # Ranked
        2  # Approved
    ]

    if not exclude_approved:
        allowed_status.extend([
            3, # Qualified
            4  # Loved
        ])

    return session.query(DBScore) \
        .join(DBScore.beatmap) \
        .filter(DBBeatmap.status.in_(allowed_status)) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .order_by(DBScore.pp.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_top_scores_count(
    user_id: int,
    mode: int,
    session: Session = ...
) -> int:
    return session.query(func.count(DBScore.id)) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .scalar()

@session_wrapper
def fetch_leader_scores(
    user_id: int,
    mode: int,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBScore]:
    # Find the maximum total score for each beatmap
    subquery = session.query(
            DBScore.beatmap_id,
            DBScore.mode,
            func.max(DBScore.total_score).label('max_total_score')
        ) \
        .join(DBScore.beatmap) \
        .filter(DBBeatmap.status > 0) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .group_by(DBScore.beatmap_id, DBScore.mode) \
        .subquery()

    # Get scores where the user has the highest total score
    return session.query(DBScore) \
        .join(subquery, and_(
            DBScore.beatmap_id == subquery.c.beatmap_id,
            DBScore.mode == subquery.c.mode,
            DBScore.total_score == subquery.c.max_total_score
        )) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .order_by(DBScore.id.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_leader_count(
    user_id: int,
    mode: int,
    session: Session = ...
) -> int:
    # Find the maximum total score for each beatmap
    subquery = session.query(
            DBScore.beatmap_id,
            DBScore.mode,
            func.max(DBScore.total_score).label('max_total_score')
        ) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .group_by(DBScore.beatmap_id, DBScore.mode) \
        .subquery()

    # Get scores where the user has the highest total score
    return session.query(func.count(DBScore.id)) \
        .join(subquery, and_(
            DBScore.beatmap_id == subquery.c.beatmap_id,
            DBScore.mode == subquery.c.mode,
            DBScore.total_score == subquery.c.max_total_score
        )) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .scalar()

@session_wrapper
def fetch_best(
    user_id: int,
    mode: int,
    exclude_approved: bool = False,
    session: Session = ...
) -> List[DBScore]:
    allowed_status = [
        1, # Ranked
        2  # Approved
    ]

    if not exclude_approved:
        allowed_status.extend([
            3, # Qualified
            4  # Loved
        ])

    return session.query(DBScore) \
        .join(DBScore.beatmap) \
        .filter(DBBeatmap.status.in_(allowed_status)) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .order_by(DBScore.pp.desc()) \
        .all()

@session_wrapper
def fetch_pinned(
    user_id: int,
    mode: int,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .filter(DBScore.pinned == True) \
        .order_by(DBScore.pp.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_pinned_count(
    user_id: int,
    mode: int,
    session: Session = ...
) -> int:
    return session.query(func.count(DBScore.id)) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .filter(DBScore.pinned == True) \
        .scalar()

@session_wrapper
def fetch_personal_best(
    beatmap_id: int,
    user_id: int,
    mode: int,
    mods: int | None = None,
    session: Session = ...
) -> DBScore | None:
    if mods is None:
        return session.query(DBScore) \
            .options(selectinload(DBScore.user)) \
            .filter(DBScore.beatmap_id == beatmap_id) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.mode == mode) \
            .filter(DBScore.status == 3) \
            .first()

    return session.query(DBScore) \
        .options(selectinload(DBScore.user)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(or_(DBScore.status == 3, DBScore.status == 4)) \
        .filter(DBScore.mods == mods) \
        .first()

@session_wrapper
def fetch_grades(
    user_id: int,
    mode: int,
    session: Session = ...
) -> Dict[str, int]:
    grades = {
        name: 0
        for name in Grade.__members__
        if name not in ('F', 'N')
    }

    results = session.query(
            DBScore.grade,
            func.count(DBScore.id)
        ) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .filter(DBScore.grade != 'F') \
        .group_by(DBScore.grade) \
        .all()

    grades.update({grade: count for grade, count in results})
    return grades

@session_wrapper
def fetch_range_scores(
    beatmap_id: int,
    mode: int,
    offset: int = 0,
    limit: int = 5,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .options(selectinload(DBScore.user)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .order_by(DBScore.total_score.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_range_scores_country(
    beatmap_id: int,
    mode: int,
    country: str,
    limit: int = 5,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .options(selectinload(DBScore.user)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .filter(DBUser.country == country) \
        .join(DBScore.user) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_range_scores_friends(
    beatmap_id: int,
    mode: int,
    friends: List[int],
    limit: int = 5,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .options(selectinload(DBScore.user)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .filter(DBScore.user_id.in_(friends)) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_range_scores_mods(
    beatmap_id: int,
    mode: int,
    mods: int,
    limit: int = 5,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .options(selectinload(DBScore.user)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode) \
        .filter(or_(DBScore.status == 3, DBScore.status == 4)) \
        .filter(DBScore.mods == mods) \
        .order_by(DBScore.total_score.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_score_index(
    user_id: int,
    beatmap_id: int,
    mode: int,
    mods: int | None = None,
    friends: List[int] | None = None,
    country: str | None = None,
    session: Session = ...
) -> int:
    query = session.query(DBScore.user_id, DBScore.mods, func.rank() \
                .over(
                    order_by=DBScore.total_score.desc()
                ).label('rank')
            ) \
            .filter(DBScore.beatmap_id == beatmap_id) \
            .filter(DBScore.mode == mode) \
            .order_by(DBScore.total_score.desc())

    if mods != None:
        query = query.filter(DBScore.mods == mods) \
                     .filter(or_(DBScore.status == 3, DBScore.status == 4))
    else:
        query = query.filter(DBScore.status == 3)

    if country != None:
        query = query.join(DBScore.user) \
                     .filter(DBUser.country == country)

    if friends != None:
        query = query.filter(
            or_(
                DBScore.user_id.in_(friends),
                DBScore.user_id == user_id
            )
        )

    subquery = query.subquery()
    result = session.query(subquery.c.rank) \
        .filter(subquery.c.user_id == user_id) \
        .first()

    if not result:
        return 0

    return result[-1]

@session_wrapper
def fetch_score_index_by_id(
    score_id: int,
    beatmap_id: int,
    mode: int,
    mods: int | None = None,
    session: Session = ...
) -> int:
    query = session.query(DBScore.id, DBScore.mods, func.rank() \
                .over(
                    order_by=DBScore.total_score.desc()
                ).label('rank')
            ) \
            .filter(DBScore.beatmap_id == beatmap_id) \
            .filter(DBScore.mode == mode) \
            .order_by(DBScore.total_score.desc())

    if mods != None:
        query = query.filter(DBScore.mods == mods) \
                     .filter(or_(DBScore.status == 3, DBScore.status == 4))
    else:
        query = query.filter(DBScore.status == 3)

    subquery = query.subquery()
    result = session.query(subquery.c.rank) \
        .filter(subquery.c.id == score_id) \
        .first()

    if not result:
        return 0

    return result[-1]

@session_wrapper
def fetch_score_index_by_tscore(
    total_score: int,
    beatmap_id: int,
    mode: int,
    session: Session = ...
) -> int:
    closest_score = session.query(DBScore) \
        .filter(DBScore.total_score > total_score) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .order_by(func.abs(DBScore.total_score - total_score)) \
        .first()

    if not closest_score:
        return 1

    # Fetch score rank for closest score
    return fetch_score_index_by_id(
        closest_score.id,
        beatmap_id,
        mode
    ) + 1

@session_wrapper
def fetch_score_above(
    beatmap_id: int,
    mode: int,
    total_score: int,
    session: Session = ...
) -> DBScore | None:
    return session.query(DBScore) \
        .options(selectinload(DBScore.user)) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.total_score > total_score) \
        .filter(DBScore.status == 3) \
        .order_by(DBScore.total_score.asc()) \
        .first()

@session_wrapper
def fetch_recent(
    user_id: int,
    mode: int,
    limit: int = 3,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .order_by(DBScore.id.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_recent_until(
    user_id: int,
    mode: int,
    until: datetime,
    min_status: int = 2,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .filter(DBScore.submitted_at > until) \
        .filter(DBScore.status >= min_status) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .order_by(DBScore.id.desc()) \
        .all()

@session_wrapper
def fetch_recent_all(
    user_id: int,
    limit: int = 3,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .filter(DBScore.user_id == user_id) \
        .order_by(DBScore.id.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_recent_top_scores(
    user_id: int,
    limit: int = 3,
    session: Session = ...
) -> List[DBScore]:
    return session.query(DBScore) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.status == 3) \
        .order_by(DBScore.id.desc()) \
        .limit(limit) \
        .all()

@session_wrapper
def fetch_pp_record(
    mode: int,
    mods: int | None = None,
    session: Session = ...
) -> DBScore:
    if mods == None:
        return session.query(DBScore) \
                .filter(DBScore.mode == mode) \
                .filter(DBScore.status > 2) \
                .order_by(DBScore.pp.desc()) \
                .first()

    return session.query(DBScore) \
            .filter(DBScore.mode == mode) \
            .filter(DBScore.status > 2) \
            .filter(DBScore.mods == mods) \
            .order_by(DBScore.pp.desc()) \
            .first()

@session_wrapper
def fetch_clears(
    user_id: int,
    mode: int,
    session: Session = ...
) -> int:
    return session.query(func.count(DBScore.id)) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.mode == mode) \
        .filter(DBScore.status == 3) \
        .scalar()

@session_wrapper
def delete(score_id: int, session: Session = ...):
    session.query(DBScore) \
        .filter(DBScore.id == score_id) \
        .delete()
    session.commit()

@session_wrapper
def delete_by_beatmap_id(beatmap_id: int, session: Session = ...):
    session.query(DBScore) \
        .filter(DBScore.beatmap_id == beatmap_id) \
        .delete()
    session.commit()

@session_wrapper
def restore_hidden_scores(user_id: int, session: Session = ...):
    """This will restore all score status attributes"""
    app.session.logger.info(f'Restoring scores for user: {user_id}...')

    # Set failed scores to status 1
    session.query(DBScore) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.failtime != None) \
            .filter(DBScore.status == -1) \
            .update({
                'status': 1
            })
    session.commit()

    # Fetch remaining scores, that are submitted
    user_scores = session.query(DBScore) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.failtime == None) \
            .filter(DBScore.status == -1) \
            .all()

    if not user_scores:
        return

    # Sort scores by beatmap id
    scores_dict = defaultdict(list)

    for score in user_scores:
        scores_dict[score.beatmap_id].append(score)

    for beatmap_id, beatmap_scores in scores_dict.items():
        # Sort scores by pp
        beatmap_scores.sort(key=lambda x: x.pp, reverse=True)

        # Update best score
        best_score = beatmap_scores[0]
        update(best_score.id, {'status': 3}, session=session)

        # Sort scores by mods
        mods_dict = defaultdict(list)

        for score in beatmap_scores:
            mods_dict[score.mods].append(score)

        for mods, scores_list in mods_dict.items():
            # Sort scores by pp
            scores_list.sort(key=lambda x: x.pp, reverse=True)

            # Get best score with mods
            mods_best_score = scores_list.pop(0)

            # Update other scores to submitted status
            for score in scores_list:
                best_score_ids = (mods_best_score.id, best_score.id)

                if score.id in best_score_ids:
                    continue

                update(score.id, {'status': 2}, session=session)

            if mods == best_score.mods:
                # Don't update the best score
                continue

            # Update best mod-score
            update(mods_best_score.id, {'status': 4}, session=session)

    app.session.logger.info('Scores have been restored!')
