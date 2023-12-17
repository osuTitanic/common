
from ..objects import DBVerification
from typing import Optional, List

import random
import string
import app

def create(user_id: int, type: int, token_size: int = 32) -> DBVerification:
    with app.session.database.managed_session() as session:
        session.add(
            v := DBVerification(
                ''.join(random.choices(
                    string.ascii_lowercase +
                    string.digits, k=token_size
                )),
                user_id,
                type
            )
        )
        session.commit()
        session.refresh(v)

    return v

def fetch_by_id(id: int) -> Optional[DBVerification]:
    with app.session.database.managed_session() as session:
        return session.query(DBVerification) \
            .filter(DBVerification.id == id) \
            .first()

def fetch_by_token(token: str) -> Optional[DBVerification]:
    with app.session.database.managed_session() as session:
        return session.query(DBVerification) \
            .filter(DBVerification.token == token) \
            .first()

def fetch_all(user_id: int) -> List[DBVerification]:
    with app.session.database.managed_session() as session:
        return session.query(DBVerification) \
            .filter(DBVerification.user_id == user_id) \
            .all()

def fetch_all_by_type(user_id: int, verification_type: int) -> List[DBVerification]:
    with app.session.database.managed_session() as session:
        return session.query(DBVerification) \
            .filter(DBVerification.user_id == user_id) \
            .filter(DBVerification.type == verification_type) \
            .all()

def delete(token: str) -> int:
    with app.session.database.managed_session() as session:
        rows = session.query(DBVerification) \
                .filter(DBVerification.token == token) \
                .delete()
        session.commit()

    return rows
