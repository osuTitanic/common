


from __future__ import annotations

from app.common.database.objects import DBRelease
from sqlalchemy.orm import Session
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    version: int,
    downloads: list,
    hashes: dict,
    screenshots: dict,
    session: Session = ...
) -> DBRelease:
    session.add(
        release := DBRelease(
            name=name,
            version=version,
            hashes=hashes
        )
    )
    session.refresh(release)
    session.commit()
    return release

@session_wrapper
def fetch_by_name(name: str, session: Session = ...) -> DBRelease | None:
    return session.query(DBRelease) \
        .filter(DBRelease.name == name) \
        .first()

@session_wrapper
def fetch_by_version(version: int, session: Session = ...) -> DBRelease | None:
    return session.query(DBRelease) \
        .filter(DBRelease.version == version) \
        .first()

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBRelease]:
    return session.query(DBRelease) \
        .order_by(DBRelease.version.desc()) \
        .all()

@session_wrapper
def fetch_hashes(version: int, session: Session = ...) -> List[dict]:
    return session.query(DBRelease.hashes) \
        .filter(DBRelease.version == version) \
        .all()
