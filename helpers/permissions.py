
from app.common.database import permissions, groups
from app.common.helpers import caching
from typing import List, Tuple

def fetch_all(user_id: int) -> Tuple[List[str], List[str]]:
    granted, rejected = cached_user_permissions(user_id)
    user_groups = cached_groups(user_id)

    for group in user_groups:
        group_granted, group_rejected = cached_group_permissions(group.id)
        granted.extend(group_granted)
        rejected.extend(group_rejected)

    return granted, rejected

def includes_permission(permission: str, permissions: List[str]) -> bool:
    for entry in permissions:
        if entry == permission:
            return True

        if entry == '*':
            return True

        if not entry.endswith('.*'):
            continue

        if permission.startswith(entry[:-2]):
            return True
        
    return False

def is_granted(permission: str, user_id: int) -> bool:
    permission = permission.lower().removesuffix('.*')
    granted, rejected = fetch_all(user_id)
    return includes_permission(permission, granted)

def is_rejected(permission: str, user_id: int) -> bool:
    permission = permission.lower().removesuffix('.*')
    granted, rejected = fetch_all(user_id)
    return includes_permission(permission, rejected)

def has_permission(permission: str, user_id: int) -> bool:
    permission = permission.lower().removesuffix('.*')
    granted, rejected = fetch_all(user_id)

    return (
        includes_permission(permission, granted) and not
        includes_permission(permission, rejected)
    )

@caching.ttl_cache(ttl=60*15)
def cached_group_permissions(group_id: int) -> Tuple[List[str], List[str]]:
    return permissions.fetch_group_permissions(group_id)

@caching.ttl_cache(ttl=60)
def cached_user_permissions(user_id: int) -> Tuple[List[str], List[str]]:
    return permissions.fetch_user_permissions(user_id)

@caching.ttl_cache(ttl=60)
def cached_groups(user_id: int) -> List[str]:
    return groups.fetch_user_groups(user_id, True)
