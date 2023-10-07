
import app

def set(count: int) -> None:
    app.session.redis.set(
        'bancho:users',
        count
    )

def get() -> int:
    if not (count := app.session.redis.get('bancho:users')):
        return 0

    return int(count)

def increment(amount: int = 1) -> None:
    app.session.redis.incr(
        'bancho:users',
        amount
    )

def decrement(amount: int = 1) -> None:
    app.session.redis.decr(
        'bancho:users',
        amount
    )
