
from __future__ import annotations

from ..constants import COUNTRIES as countries
from ..database.repositories import users, modding, scores
from ..database.objects import DBStats

from typing import Tuple, List, Optional
from sqlalchemy.orm import Session

import app

def update(stats: DBStats, country: str) -> None:
    """Update ppv1, ppv2, country and score ranks"""
    # Performance
    app.session.redis.zadd(
        f'bancho:performance:{stats.mode}',
        {stats.user_id: float(stats.pp)}
    )

    app.session.redis.zadd(
        f'bancho:performance:{stats.mode}:{country.lower()}',
        {stats.user_id: float(stats.pp)}
    )

    # Ranked Score
    app.session.redis.zadd(
        f'bancho:rscore:{stats.mode}',
        {stats.user_id: stats.rscore}
    )

    app.session.redis.zadd(
        f'bancho:rscore:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.rscore}
    )

    # Total Score
    app.session.redis.zadd(
        f'bancho:tscore:{stats.mode}',
        {stats.user_id: stats.tscore}
    )

    app.session.redis.zadd(
        f'bancho:tscore:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.tscore}
    )

    # PPV1
    app.session.redis.zadd(
        f'bancho:ppv1:{stats.mode}',
        {stats.user_id: stats.ppv1}
    )

    app.session.redis.zadd(
        f'bancho:ppv1:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.ppv1}
    )

    # Accuracy
    app.session.redis.zadd(
        f'bancho:acc:{stats.mode}',
        {stats.user_id: stats.acc}
    )

    app.session.redis.zadd(
        f'bancho:acc:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.acc}
    )

    clears = sum([
        stats.xh_count,
        stats.x_count,
        stats.sh_count,
        stats.s_count,
        stats.a_count,
        stats.b_count,
        stats.c_count,
        stats.d_count
    ])

    # Clears
    app.session.redis.zadd(
        f'bancho:clears:{stats.mode}',
        {stats.user_id: clears}
    )

    app.session.redis.zadd(
        f'bancho:clears:{stats.mode}:{country.lower()}',
        {stats.user_id: clears}
    )

    # PP VN
    app.session.redis.zadd(
        f'bancho:ppvn:{stats.mode}',
        {stats.user_id: stats.pp_vn}
    )

    app.session.redis.zadd(
        f'bancho:ppvn:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.pp_vn}
    )

    # PP RX
    app.session.redis.zadd(
        f'bancho:pprx:{stats.mode}',
        {stats.user_id: stats.pp_rx}
    )

    app.session.redis.zadd(
        f'bancho:pprx:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.pp_rx}
    )

    # PP AP
    app.session.redis.zadd(
        f'bancho:ppap:{stats.mode}',
        {stats.user_id: stats.pp_ap}
    )

    app.session.redis.zadd(
        f'bancho:ppap:{stats.mode}:{country.lower()}',
        {stats.user_id: stats.pp_ap}
    )

def update_leader_scores(stats: DBStats, country: str, session: Optional[Session] = None) -> None:
    """Update #1 count"""
    count = scores.fetch_leader_count(
        stats.user_id,
        stats.mode,
        session=session
    )

    app.session.redis.zadd(
        f'bancho:leader:{stats.mode}',
        {stats.user_id: count}
    )

    app.session.redis.zadd(
        f'bancho:leader:{stats.mode}:{country.lower()}',
        {stats.user_id: count}
    )

def update_kudosu(user_id: int, country: str, session: Optional[Session] = None) -> None:
    """Update #1 count"""
    kudosu = modding.total_amount_by_user(
        user_id,
        session=session
    )

    app.session.redis.zadd(
        f'bancho:kudosu',
        {user_id: kudosu}
    )

    app.session.redis.zadd(
        f'bancho:kudosu:{country.lower()}',
        {user_id: kudosu}
    )

def remove_country(
    user_id: int,
    country: str
) -> None:
    """Remove player from country leaderboards"""
    for mode in range(4):
        app.session.redis.zrem(
            f'bancho:performance:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:rscore:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:tscore:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppv1:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:acc:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:clears:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppvn:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:pprx:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppap:{mode}:{country.lower()}',
            user_id
        )

def remove(
    user_id: int,
    country: str
) -> None:
    """Remove player from leaderboards"""
    for mode in range(4):
        app.session.redis.zrem(
            f'bancho:performance:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:performance:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:rscore:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:rscore:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:tscore:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:tscore:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppv1:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppv1:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:acc:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:acc:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:clears:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:clears:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppvn:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppvn:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:pprx:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:pprx:{mode}:{country.lower()}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppap:{mode}',
            user_id
        )

        app.session.redis.zrem(
            f'bancho:ppap:{mode}:{country.lower()}',
            user_id
        )

def global_rank(
    user_id: int,
    mode: int
) -> int:
    """Get global rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:performance:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def ppv1_rank(
    user_id: int,
    mode: int
) -> int:
    """Get ppv1 rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:ppv1:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def country_rank(
    user_id: int,
    mode: int,
    country: str
) -> int:
    """Get country rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:performance:{mode}:{country.lower()}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def score_rank(
    user_id: int,
    mode: int
) -> int:
    """Get score rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:rscore:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def clears_rank(
    user_id: int,
    mode: int
) -> int:
    """Get clears rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:clears:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def total_score_rank(
    user_id: int,
    mode: int
) -> int:
    """Get total score rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:tscore:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def score_rank_country(
    user_id: int,
    mode: int,
    country: str
) -> int:
    """Get score rank by country"""
    rank = app.session.redis.zrevrank(
        f'bancho:rscore:{mode}:{country.lower()}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def clears_rank_country(
    user_id: int,
    mode: int,
    country: str
) -> int:
    """Get clears rank by country"""
    rank = app.session.redis.zrevrank(
        f'bancho:clears:{mode}:{country.lower()}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def ppv1_country_rank(
    user_id: int,
    mode: int,
    country: str
) -> int:
    """Get country ppv1 rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:ppv1:{mode}:{country.lower()}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def total_score_rank_country(
    user_id: int,
    mode: int,
    country: str
) -> int:
    """Get total score rank by country"""
    rank = app.session.redis.zrevrank(
        f'bancho:tscore:{mode}:{country.lower()}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def vn_pp_rank(
    user_id: int,
    mode: int
) -> int:
    """Get vn pp rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:ppvn:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def rx_pp_rank(
    user_id: int,
    mode: int
) -> int:
    """Get rx pp rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:pprx:{mode}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def ap_pp_rank(
    user_id: int,
    mode: int
) -> int:
    """Get ap pp rank"""
    rank = app.session.redis.zrevrank(
        f'bancho:ppap:{mode}', # lol
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def performance(
    user_id: int,
    mode: int
) -> int:
    """Get player's pp""" # this sounds wrong
    pp = app.session.redis.zscore(
        f'bancho:performace:{mode}',
        user_id
    )
    return pp if pp is not None else 0

def score(
    user_id: int,
    mode: int
) -> int:
    """Get player's ranked score"""
    score = app.session.redis.zscore(
        f'bancho:rscore:{mode}',
        user_id
    )
    return round(score) if score is not None else 0

def total_score(
    user_id: int,
    mode: int
) -> int:
    """Get player's total score"""
    score = app.session.redis.zscore(
        f'bancho:tscore:{mode}',
        user_id
    )
    return score if score is not None else 0

def clears(
    user_id: int,
    mode: int
) -> int:
    """Get player's clears"""
    clears = app.session.redis.zscore(
        f'bancho:clears:{mode}',
        user_id
    )
    return clears if clears is not None else 0

def accuracy(
    user_id: int,
    mode: int
) -> float:
    """Get player's accuracy"""
    acc = app.session.redis.zscore(
        f'bancho:acc:{mode}',
        user_id
    )
    return acc if acc is not None else 0

def ppv1(
    user_id: int,
    mode: int
) -> float:
    """Get player's ppv1"""
    pp = app.session.redis.zscore(
        f'bancho:ppv1:{mode}',
        user_id
    )
    return pp if pp is not None else 0

def vn_pp(
    user_id: int,
    mode: int
) -> float:
    """Get player's vn pp"""
    pp = app.session.redis.zscore(
        f'bancho:ppvn:{mode}',
        user_id
    )
    return pp if pp is not None else 0

def rx_pp(
    user_id: int,
    mode: int
) -> float:
    """Get player's rx pp"""
    pp = app.session.redis.zscore(
        f'bancho:pprx:{mode}',
        user_id
    )
    return pp if pp is not None else 0

def ap_pp(
    user_id: int,
    mode: int
) -> float:
    """Get player's ap pp"""
    pp = app.session.redis.zscore(
        f'bancho:ppap:{mode}',
        user_id
    )
    return pp if pp is not None else 0

def leader_scores(
    user_id: int,
    mode: int
) -> int:
    """Get player's #1 scores"""
    count = app.session.redis.zscore(
        f'bancho:leader:{mode}',
        user_id
    )
    return count if count is not None else 0

def kudosu(
    user_id: int,
    country: str | None = None
) -> int:
    """Get player's kudosu"""
    kudosu = app.session.redis.zscore(
        f'bancho:kudosu'
        f'{f":{country.lower()}" if country else ""}',
        user_id
    )
    return kudosu if kudosu is not None else 0

def rank(
    user_id: int,
    mode: int,
    type: str = 'performance',
    country: str | None = None
) -> int:
    """Get player's rank on a specific leaderboard"""
    rank = app.session.redis.zrevrank(
        f'bancho:{type}:{mode}{f":{country.lower()}" if country else ""}',
        user_id
    )
    return (rank + 1 if rank is not None else 0)

def top_players(
    mode: int,
    offset: int = 0,
    range: int = 50,
    type: str = 'performance',
    country: str | None = None
) -> List[Tuple[int, float]]:
    """Get a list of top players

    `returns`: List[Tuple[player_id, score/pp]]
    """
    players = app.session.redis.zrevrangebyscore(
        f'bancho:{type}:{mode}{f":{country.lower()}" if country else ""}',
        '+inf',
        '1',
        offset,
        range,
        withscores=True
    )

    return [(int(id), score) for id, score in players]

def top_countries(mode: int) -> List[dict]:
    """Get a list of the top countries"""
    country_rankings = []

    for country in countries.keys():
        if country == 'XX':
            continue

        country_performance = app.session.redis.zrevrangebyscore(
            f'bancho:performance:{mode}:{country.lower()}',
            '+inf',
            '1',
            withscores=True
        )

        if not country_performance:
            continue

        country_rscore = app.session.redis.zrevrangebyscore(
            f'bancho:rscore:{mode}:{country.lower()}',
            '+inf',
            '1',
            withscores=True
        )

        if not country_rscore:
            continue

        country_tscore = app.session.redis.zrevrangebyscore(
            f'bancho:tscore:{mode}:{country.lower()}',
            '+inf',
            '1',
            withscores=True
        )

        if not country_tscore:
            continue

        total_performance = sum(score for member, score in country_performance)
        total_rscore = sum(score for member, score in country_rscore)
        total_tscore = sum(score for member, score in country_tscore)
        total_users = len(country_performance)
        average_pp = total_performance / total_users

        country_rankings.append({
            'name': country.lower(),
            'total_performance': total_performance,
            'total_rscore': total_rscore,
            'total_tscore': total_tscore,
            'total_users': total_users,
            'average_pp': average_pp
        })

    country_rankings.sort(
        key=lambda x: x['total_performance'],
        reverse=True
    )

    return country_rankings

def player_count(
    mode: int,
    type: str = 'performance',
    country: str | None = None
) -> int:
    return app.session.redis.zcount(
        f'bancho:{type}:{mode}{f":{country.lower()}" if country else ""}',
        '1',
        '+inf'
    )

def player_above(
    user_id: int,
    mode: int,
    type: str = 'rscore',
) -> Tuple[int, str]:
    """Get a player above your ranked score, used in score submission response.\n
    Returns: Tuple[score, username]
    """
    position = app.session.redis.zrevrank(
        f'bancho:{type}:{mode}',
        user_id
    )

    score = app.session.redis.zscore(
        f'bancho:{type}:{mode}',
        user_id
    )

    if position is None:
        return 0, ''

    if position <= 0:
        return 0, ''

    above_id, above_score = app.session.redis.zrevrange(
        f'bancho:{type}:{mode}',
        position-1,
        position,
        withscores=True
    )[0]

    return int(above_score) - int(score), users.fetch_username(int(above_id))
