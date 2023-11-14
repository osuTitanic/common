
from ..database.objects import DBUser
from datetime import timedelta
from typing import Optional

import pickle
import app

def set_user(user: DBUser) -> None:
    app.session.redis.set(
        f'bancho:user:{user.id}',
        pickle.dumps(user),
        ex=timedelta(hours=1)
    )

def get_user(user_id: int) -> Optional[DBUser]:
    if user := app.session.redis.get(f'bancho:user:{user_id}'):
        return pickle.loads(user)

def delete_user(user_id: int) -> None:
    app.session.redis.delete(f'bancho:user:{user_id}')
