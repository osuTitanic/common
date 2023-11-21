
from app.common.database.objects import DBName
from typing import List

import app

def create(user_id: int, old_name: str) -> DBName:
    with app.session.database.session as session:
        session.add(name := DBName(user_id, old_name))
        session.commit()

    return name

def fetch_one(id: int):
    return app.session.database.session.query(DBName) \
                .filter(DBName.id == id) \
                .all()

def fetch_all(user_id: int):
    return app.session.database.session.query(DBName) \
                .filter(DBName.user_id == user_id) \
                .all()
