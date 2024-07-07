from __future__ import annotations

from app.common.database.objects import DBBenchmark
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    user_id: int,
    smoothness: float,
    framerate: int,
    score: int,
    grade: str,
    session: Session = ...
) -> DBBenchmark:
    session.add(
        bench := DBBenchmark(
            user_id=user_id,
            smoothness=smoothness,
            framerate=framerate,
            score=score,
            grade=grade
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