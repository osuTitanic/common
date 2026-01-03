
from __future__ import annotations

from app.common.database.objects import DBVerification
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

import random
import string

@session_wrapper
def create(
    user_id: int,
    type: int,
    token_size: int = 32,
    session: Session = ...
) -> DBVerification:
    session.add(
        v := DBVerification(
            token=''.join(random.choices(
                string.ascii_lowercase +
                string.digits, k=token_size
            )),
            user_id=user_id,
            type=type,
            sent_at=datetime.now()
        )
    )
    session.flush()
    session.refresh(v)
    return v

@session_wrapper
def fetch_by_id(id: int, session: Session = ...) -> DBVerification | None:
    return session.query(DBVerification) \
        .filter(DBVerification.id == id) \
        .first()

@session_wrapper
def fetch_by_token(token: str, session: Session = ...) -> DBVerification | None:
    return session.query(DBVerification) \
        .filter(DBVerification.token == token) \
        .first()

@session_wrapper
def fetch_all(user_id: int, session: Session = ...) -> List[DBVerification]:
    return session.query(DBVerification) \
        .filter(DBVerification.user_id == user_id) \
        .all()

@session_wrapper
def fetch_all_by_type(
    user_id: int,
    verification_type: int,
    session: Session = ...
) -> List[DBVerification]:
    return session.query(DBVerification) \
        .filter(DBVerification.user_id == user_id) \
        .filter(DBVerification.type == verification_type) \
        .all()

@session_wrapper
def delete(token: str, session: Session = ...) -> int:
    rows = session.query(DBVerification) \
            .filter(DBVerification.token == token) \
            .delete()
    session.flush()
    return rows
