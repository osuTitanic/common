
from __future__ import annotations

from app.common.database.objects import DBUserPermission, DBGroupPermission
from sqlalchemy.orm import Session
from typing import List, Tuple

from .wrapper import session_wrapper

@session_wrapper
def create_user_permission(
    user_id: int,
    permission: str,
    rejected: bool = False,
    session: Session = ...
) -> DBUserPermission:
    session.add(
        user_permission := DBUserPermission(
            user_id=user_id,
            permission=permission,
            rejected=rejected
        )
    )
    session.commit()
    session.refresh(user_permission)
    return user_permission

@session_wrapper
def create_group_permission(
    group_id: int,
    permission: str,
    rejected: bool = False,
    session: Session = ...
) -> DBGroupPermission:
    session.add(
        group_permission := DBGroupPermission(
            group_id=group_id,
            permission=permission,
            rejected=rejected
        )
    )
    session.commit()
    session.refresh(group_permission)
    return group_permission

@session_wrapper
def fetch_user_permissions(
    user_id: int,
    session: Session
) -> Tuple[List[str], List[str]]:
    granted = session.query(DBUserPermission.permission) \
        .filter(DBUserPermission.user_id == user_id) \
        .filter(DBUserPermission.rejected == False) \
        .all()

    rejected = session.query(DBUserPermission.permission) \
        .filter(DBUserPermission.user_id == user_id) \
        .filter(DBUserPermission.rejected == True) \
        .all()

    return (
        [permission for (permission,) in granted],
        [permission for (permission,) in rejected]
    )

@session_wrapper
def fetch_group_permissions(
    group_id: int,
    session: Session
) -> Tuple[List[str], List[str]]:
    granted = session.query(DBGroupPermission.permission) \
        .filter(DBGroupPermission.group_id == group_id) \
        .filter(DBGroupPermission.rejected == False) \
        .all()

    rejected = session.query(DBGroupPermission.permission) \
        .filter(DBGroupPermission.group_id == group_id) \
        .filter(DBGroupPermission.rejected == True) \
        .all()

    return (
        [permission for (permission,) in granted],
        [permission for (permission,) in rejected]
    )
