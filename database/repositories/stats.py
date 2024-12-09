
from __future__ import annotations

from app.common.database.objects import (
    DBReplayHistory,
    DBBeatmap,
    DBStats,
    DBScore
)

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from .wrapper import session_wrapper
from . import scores

import config

@session_wrapper
def create(
    user_id: int,
    mode: int,
    session: Session = ...
) -> DBStats:
    session.add(
        stats := DBStats(
            user_id,
            mode
        )
    )
    session.commit()
    session.refresh(stats)
    return stats

@session_wrapper
def update(
    user_id: int,
    mode: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBStats) \
           .filter(DBStats.user_id == user_id) \
           .filter(DBStats.mode == mode) \
           .update(updates)
    session.commit()
    return rows

@session_wrapper
def update_all(
    user_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBStats) \
           .filter(DBStats.user_id == user_id) \
           .update(updates)
    session.commit()
    return rows

@session_wrapper
def delete_all(user_id: int, session: Session = ...) -> int:
    rows = session.query(DBStats) \
            .filter(DBStats.user_id == user_id) \
            .delete()
    session.commit()
    return rows

@session_wrapper
def fetch_by_mode(
    user_id: int,
    mode: int,
    session: Session = ...
) -> DBStats | None:
    return session.query(DBStats) \
        .filter(DBStats.user_id == user_id) \
        .filter(DBStats.mode == mode) \
        .first()

@session_wrapper
def fetch_all(user_id: int, session: Session = ...) -> List[DBStats]:
    return session.query(DBStats) \
        .filter(DBStats.user_id == user_id) \
        .all()

@session_wrapper
def restore(user_id: int, session: Session = ...) -> None:
    """Recalculate stats from scratch"""
    all_stats = [
        DBStats(user_id, mode)
        for mode in range(4)
    ]

    for mode in range(4):
        score_count = session.query(DBScore) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.mode == mode) \
            .count()

        fail_times = session.query(
            func.sum(DBScore.failtime)
        ) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.mode == mode) \
            .filter(DBScore.status_pp == 1) \
            .scalar()

        fail_times = (fail_times / 1000) \
            if fail_times else 0

        map_times = session.query(
            DBScore,
            func.sum(DBBeatmap.total_length)
        ) \
            .join(DBBeatmap) \
            .group_by(DBScore) \
            .filter(DBScore.user_id == 15) \
            .filter(DBScore.mode == 0) \
            .filter(DBScore.status_pp > 1) \
            .first() or [0]

        playtime = map_times[-1] + fail_times

        combo_score = session.query(DBScore) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.mode == mode) \
            .filter(DBScore.hidden == False) \
            .order_by(DBScore.max_combo.desc()) \
            .first()

        max_combo = (
            combo_score.max_combo
            if combo_score else 0
        )

        total_score = session.query(
            func.sum(DBScore.total_score)
        ) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.hidden == False) \
            .filter(DBScore.mode == mode) \
            .scalar() or 0

        stats: DBStats = all_stats[mode]
        stats.playcount = score_count
        stats.max_combo = max_combo
        stats.tscore = total_score
        stats.playtime = playtime

        top_scores = scores.fetch_top_scores(
            user_id,
            mode,
            exclude_approved=(not config.APPROVED_MAP_REWARDS)
        )

        if top_scores:
            # Update accuracy
            total_acc = 0
            divide_total = 0

            for index, s in enumerate(top_scores):
                add = 0.95 ** index
                total_acc += s.acc * add
                divide_total += add

            stats.acc = (
                total_acc / divide_total
                if divide_total != 0 else 0.0
            )

            # Update pp
            weighted_pp = sum(score.pp * 0.95**index for index, score in enumerate(top_scores))
            bonus_pp = 416.6667 * (1 - 0.9994**len(top_scores))
            stats.pp = weighted_pp + bonus_pp

            # Update rscore
            stats.rscore = sum(
                score.total_score for score in top_scores
            )

        # Update grades
        grades = scores.fetch_grades(
            stats.user_id,
            stats.mode,
            session=session
        )

        for grade, count in grades.items():
            setattr(
                stats,
                f'{grade.lower()}_count',
                count
            )

        # Update total hits
        total_hits_formula = {
            0: DBScore.n50 + DBScore.n100 + DBScore.n300,
            1: DBScore.n50 + DBScore.n100 + DBScore.n300,
            2: DBScore.n50 + DBScore.n100 + DBScore.n300 + DBScore.nKatu,
            3: DBScore.n50 + DBScore.n100 + DBScore.n300 + DBScore.nKatu + DBScore.nGeki
        }

        stats.total_hits = session.query(
            func.sum(total_hits_formula[stats.mode])
        ) \
            .filter(DBScore.user_id == stats.user_id) \
            .filter(DBScore.mode == stats.mode) \
            .filter(DBScore.hidden == False) \
            .scalar() or 0

        # Update replay views
        stats.replay_views = session.query(
            func.sum(DBReplayHistory.replay_views)
        ) \
            .filter(DBReplayHistory.user_id == stats.user_id) \
            .filter(DBReplayHistory.mode == stats.mode) \
            .scalar() or 0

    for stats in all_stats:
        session.add(stats)

    session.commit()
