
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
    session.flush()
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
    session.flush()
    session.refresh(group_permission)
    return group_permission

@session_wrapper
def create_many_for_user(
    user_id: int,
    permissions: List[str],
    rejected: bool = False,
    session: Session = ...
) -> List[DBUserPermission]:
    user_permissions = [
        DBUserPermission(
            user_id=user_id,
            permission=permission,
            rejected=rejected
        )
        for permission in permissions
    ]
    session.add_all(user_permissions)
    session.flush()
    session.flush()
    return user_permissions

@session_wrapper
def create_many_for_group(
    group_id: int,
    permissions: List[str],
    rejected: bool = False,
    session: Session = ...
) -> List[DBGroupPermission]:
    group_permissions = [
        DBGroupPermission(
            group_id=group_id,
            permission=permission,
            rejected=rejected
        )
        for permission in permissions
    ]
    session.add_all(group_permissions)
    session.flush()
    session.flush()
    return group_permissions

@session_wrapper
def fetch_user_permissions(
    user_id: int,
    session: Session = ...
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
    session: Session = ...
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

@session_wrapper
def delete_user_permission(
    user_id: int,
    permission: str,
    session: Session = ...
) -> None:
    session.query(DBUserPermission) \
        .filter(DBUserPermission.user_id == user_id) \
        .filter(DBUserPermission.permission == permission) \
        .delete()
    session.flush()

@session_wrapper
def delete_group_permission(
    group_id: int,
    permission: str,
    session: Session = ...
) -> None:
    session.query(DBGroupPermission) \
        .filter(DBGroupPermission.group_id == group_id) \
        .filter(DBGroupPermission.permission == permission) \
        .delete()
    session.flush()

@session_wrapper
def delete_many_for_user(
    user_id: int,
    permissions: List[str],
    session: Session = ...
) -> None:
    session.query(DBUserPermission) \
        .filter(DBUserPermission.user_id == user_id) \
        .filter(DBUserPermission.permission.in_(permissions)) \
        .delete()
    session.flush()

@session_wrapper
def delete_many_for_group(
    group_id: int,
    permissions: List[str],
    session: Session = ...
) -> None:
    session.query(DBGroupPermission) \
        .filter(DBGroupPermission.group_id == group_id) \
        .filter(DBGroupPermission.permission.in_(permissions)) \
        .delete()
    session.flush()
