
import app

def set_osu(count: int) -> None:
    app.session.redis.set('bancho:activity:osu', max(0, count))

def get_osu() -> int:
    return int(app.session.redis.get('bancho:activity:osu') or b"0")

def set_irc(count: int) -> None:
    app.session.redis.set('bancho:activity:irc', max(0, count))

def get_irc() -> int:
    return int(app.session.redis.get('bancho:activity:irc') or b"0")

def set_mp(count: int) -> None:
    app.session.redis.set('bancho:activity:mp', max(0, count))

def get_mp() -> int:
    return int(app.session.redis.get('bancho:activity:mp') or b"0")

def set_all(
    osu_count: int | None = None,
    irc_count: int | None = None,
    mp_count: int | None = None
) -> None:
    with app.session.redis.pipeline() as pipe:
        if osu_count is not None:
            pipe.set('bancho:activity:osu', max(0, osu_count))
        if irc_count is not None:
            pipe.set('bancho:activity:irc', max(0, irc_count))
        if mp_count is not None:
            pipe.set('bancho:activity:mp', max(0, mp_count))
        pipe.execute()

def get_all() -> dict[str, int]:
    values = app.session.redis.mget(
        'bancho:activity:osu',
        'bancho:activity:irc',
        'bancho:activity:mp'
    )
    return {
        'osu': int(values[0] or b"0"),
        'irc': int(values[1] or b"0"),
        'mp': int(values[2] or b"0")
    }
