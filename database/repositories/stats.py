
from __future__ import annotations

from app.common.database.objects import (
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
    all_stats = [DBStats(user_id, mode) for mode in range(4)]

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
            .filter(DBScore.status == 1) \
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
            .filter(DBScore.status > 1) \
            .first()

        if map_times:
            map_times = map_times[-1]
        else:
            map_times = 0

        playtime = map_times + fail_times

        combo_score = session.query(DBScore) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.mode == mode) \
            .order_by(DBScore.max_combo.desc()) \
            .first()

        if combo_score:
            max_combo = combo_score.max_combo
        else:
            max_combo = 0

        total_score = session.query(
            func.sum(DBScore.total_score)
        ) \
            .filter(DBScore.user_id == user_id) \
            .filter(DBScore.mode == mode) \
            .scalar()

        if total_score is None:
            total_score = 0

        stats: DBStats = all_stats[mode]
        stats.playcount = score_count
        stats.max_combo = max_combo
        stats.tscore = total_score
        stats.playtime = playtime

        top_scores = scores.fetch_top_scores(
            user_id,
            mode,
            exclude_approved=(
                not config.APPROVED_MAP_REWARDS
            )
        )

        # Update acc and pp

        score_count_best = scores.fetch_count(
            user_id,
            mode
        )

        if score_count_best > 0:
            total_acc = 0
            divide_total = 0

            for index, s in enumerate(top_scores):
                add = 0.95 ** index
                total_acc    += s.acc * add
                divide_total += add

            if divide_total != 0:
                stats.acc = total_acc / divide_total
            else:
                stats.acc = 0.0

            weighted_pp = sum(score.pp * 0.95**index for index, score in enumerate(top_scores))
            bonus_pp = 416.6667 * (1 - 0.9994**score_count_best)

            stats.pp = weighted_pp + bonus_pp

    best_scores = session.query(DBScore) \
        .filter(DBScore.user_id == user_id) \
        .filter(DBScore.status == 3) \
        .all()

    for score in best_scores:
        stats: DBStats = all_stats[score.mode]

        grade_count = eval(f'stats.{score.grade.lower()}_count')

        if not grade_count:
            grade_count = 0

        if not stats.rscore:
            stats.rscore = 0

        if not stats.total_hits:
            stats.total_hits = 0

        stats.rscore += score.total_score
        grade_count += 1

        if stats.mode == 2:
            # ctb
            total_hits = score.n50 + score.n100 + score.n300 + score.nMiss + score.nKatu

        elif stats.mode == 3:
            # mania
            total_hits = score.n300 + score.n100 + score.n50 + score.nGeki + score.nKatu + score.nMiss

        else:
            # standard + taiko
            total_hits = score.n50 + score.n100 + score.n300 + score.nMiss

        stats.total_hits += total_hits

    for stats in all_stats:
        session.add(stats)

    session.commit()
