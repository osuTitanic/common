from __future__ import annotations

from app.common.database.objects import DBBenchmark
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    smoothness: float,
    framerate: int,
    score: int,
    grade: str,
    client: str,
    hardware: dict,
    session: Session = ...
) -> DBBenchmark:
    session.add(
        bench := DBBenchmark(
            user_id=user_id,
            smoothness=smoothness,
            framerate=framerate,
            score=score,
            grade=grade,
            client=client
            hardware=hardware
        )
    )
    session.commit()
    return bench

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> DBBenchmark | None:
    return session.query(DBBenchmark) \
        .filter(DBBenchmark.id == id) \
        .first()

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBBenchmark]:
    return session.query(DBBenchmark) \
        .all()

@session_wrapper
def fetch_range(
    offset: int,
    limit: int,
    session: Session = ...
) -> List[DBBenchmark]:
    return session.query(DBBenchmark) \
        .order_by(DBBenchmark.score.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

@session_wrapper
def delete(benchmark_id: int, session: Session = ...) -> int:
    rows = session.query(DBBenchmark) \
        .filter(DBBenchmark.id == benchmark_id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def update(
    benchmark_id: int,
    update: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBBenchmark) \
        .filter(DBBenchmark.id == benchmark_id) \
        .update(update)
    session.commit()
    return rows

@session_wrapper
def fetch_leaderboard(
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBBenchmark]:
    # Create subquery to get max score per user
    subquery = session.query(
        DBBenchmark.user_id,
        func.max(DBBenchmark.score).label('max_score')
    ).group_by(
        DBBenchmark.user_id
    ).subquery()

    # Get benchmarks with max score per user
    query = session.query(DBBenchmark) \
        .join(subquery, and_(
            DBBenchmark.user_id == subquery.c.user_id,
            DBBenchmark.score == subquery.c.max_score
        )) \
        .order_by(DBBenchmark.score.desc()) \
        .offset(offset) \
        .limit(limit) \
        .all()

    return query
