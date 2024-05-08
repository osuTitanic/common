
from sqlalchemy.orm import Session
from functools import wraps
from functools import wraps

import app

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
