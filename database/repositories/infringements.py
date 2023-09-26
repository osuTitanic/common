
from app.common.database import DBInfringement
from typing import Optional, List

import app

def create(
    user_id: int,
    action: int,
    length: datetime,
    description: Optional[str] = None,
    is_permanent: bool = False
) -> DBInfringement:
    ...

def fetch_recent(user_id: int) -> Optional[DBInfringement]:
    ...

def fetch_recent_by_action(user_id: int, action: int) -> List[DBInfringement]:
    ...

def fetch_all(user_id: int) -> List[DBInfringement]:
    ...

def fetch_all_by_action(user_id: int, action: int) -> List[DBInfringement]:
    ...
