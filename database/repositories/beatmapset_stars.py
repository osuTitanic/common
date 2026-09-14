
from .wrapper import SessionProvider, session_wrapper
from ..objects import DBBeatmapsetStar
from sqlalchemy.orm import Session

@session_wrapper
def create(
    set_id: int,
    user_id: int,
    session: Session = SessionProvider,
) -> DBBeatmapsetStar:
    star = DBBeatmapsetStar(
        set_id=set_id,
        user_id=user_id,
        kudosu_cost=1,
        star_priority=1,
    )
    session.add(star)
    session.flush()
    session.refresh(star)
    return star
