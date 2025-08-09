
from __future__ import annotations

from app.common.cache import leaderboards
from app.common.database.objects import (
    DBReplayHistory,
    DBPlayHistory,
    DBRankHistory,
    DBStats
)

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def update_plays(
    user_id: int,
    mode: int,
    session: Session = ...
) -> None:
    time = datetime.now()

    updated = session.query(DBPlayHistory) \
            .filter(DBPlayHistory.user_id == user_id) \
            .filter(DBPlayHistory.mode == mode) \
            .filter(DBPlayHistory.year == time.year) \
            .filter(DBPlayHistory.month == time.month) \
            .update({
                'plays': DBPlayHistory.plays + 1
            })

    if not updated:
        session.add(
            DBPlayHistory(
                user_id,
                mode,
                plays=1
            )
        )

    session.commit()

@session_wrapper
def fetch_plays_history(
    user_id: int,
    mode: int,
    until: datetime,
    session: Session = ...
) -> List[DBPlayHistory]:
    return session.query(DBPlayHistory) \
        .filter(DBPlayHistory.user_id == user_id) \
        .filter(DBPlayHistory.mode == mode) \
        .filter(or_(
            DBPlayHistory.year >= until.year,
            DBPlayHistory.month >= until.month,
        )) \
        .order_by(
            DBPlayHistory.year.desc(),
            DBPlayHistory.month.desc()
        ) \
        .all()

@session_wrapper
def update_replay_views(
    user_id: int,
    mode: int,
    session: Session = ...
) -> None:
    time = datetime.now()

    updated = session.query(DBReplayHistory) \
                .filter(DBReplayHistory.user_id == user_id) \
                .filter(DBReplayHistory.mode == mode) \
                .filter(DBReplayHistory.year == time.year) \
                .filter(DBReplayHistory.month == time.month) \
                .update({
                    'replay_views': DBReplayHistory.replay_views + 1
                })

    if not updated:
        session.add(
            DBReplayHistory(
                user_id,
                mode,
                replay_views=1
            )
        )

    session.commit()

@session_wrapper
def fetch_replay_history(
    user_id: int,
    mode: int,
    until: datetime,
    session: Session = ...
) -> List[DBReplayHistory]:
    return session.query(DBReplayHistory) \
        .filter(DBReplayHistory.user_id == user_id) \
        .filter(DBReplayHistory.mode == mode) \
        .filter(or_(
            DBReplayHistory.year >= until.year,
            DBReplayHistory.month >= until.month,
        )) \
        .order_by(
            DBReplayHistory.year.desc(),
            DBReplayHistory.month.desc()
        ) \
        .all()

@session_wrapper
def update_rank(
    stats: DBStats,
    country: str,
    session: Session = ...
) -> None:
    country_rank = leaderboards.country_rank(stats.user_id, stats.mode, country)
    global_rank = leaderboards.global_rank(stats.user_id, stats.mode)
    score_rank = leaderboards.score_rank(stats.user_id, stats.mode)
    ppv1_rank = leaderboards.ppv1_rank(stats.user_id, stats.mode)

    pp_vn_rank = leaderboards.vn_pp_rank(stats.user_id, stats.mode)
    pp_rx_rank = leaderboards.rx_pp_rank(stats.user_id, stats.mode)
    pp_ap_rank = leaderboards.ap_pp_rank(stats.user_id, stats.mode)

    if any([
        global_rank <= 0,
        country_rank <= 0,
        score_rank <= 0,
        ppv1_rank <= 0,
    ]):
        return

    session.add(
        DBRankHistory(
            stats.user_id,
            stats.mode,
            stats.rscore,
            stats.pp,
            stats.ppv1,
            stats.pp_vn,
            stats.pp_rx,
            stats.pp_ap,
            global_rank,
            country_rank,
            score_rank,
            ppv1_rank,
            pp_vn_rank,
            pp_rx_rank,
            pp_ap_rank
        )
    )
    session.commit()

@session_wrapper
def fetch_rank_history(
    user_id: int,
    mode: int,
    until: datetime,
    session: Session = ...
) -> List[DBRankHistory]:
    return session.query(DBRankHistory) \
        .filter(DBRankHistory.user_id == user_id) \
        .filter(DBRankHistory.mode == mode) \
        .filter(DBRankHistory.time > until) \
        .order_by(DBRankHistory.time.desc()) \
        .all()

@session_wrapper
def fetch_peak_global_rank(
    user_id: int,
    mode: int,
    session: Session = ...
) -> int:
    return session.query(func.min(DBRankHistory.global_rank)) \
        .filter(DBRankHistory.user_id == user_id) \
        .filter(DBRankHistory.mode == mode) \
        .filter(DBRankHistory.global_rank != 0) \
        .scalar() or 0
