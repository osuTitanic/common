
from sqlalchemy.orm import Session
from functools import wraps
from functools import wraps
from typing import Any

import app

"""
Used with `session: Session = SessionProvider` in repository functions.
When @session_wrapper is used, this will guarantee that a session is always provided, either by the caller or by the wrapper itself.
"""
SessionProvider: Any | Session = ...

def session_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('session'):
            # Use existing session
            return func(*args, **kwargs)

        if args and isinstance(args[-1], Session):
            # Use existing session
            return func(*args, **kwargs)

        with app.session.database.managed_session() as session:
            # Get new session for this function
            kwargs['session'] = session
            return func(*args, **kwargs)

    return wrapper

# Please don't look at this mess, thanks :)
def exception_wrapper(on_fail=None):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if on_fail: return on_fail(e)
        return wrapped
    return wrapper
