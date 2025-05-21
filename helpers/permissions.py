
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

def is_granted(permission: str, user_id: int) -> bool:
    permission = permission.lower().removesuffix('.*')
    granted, rejected = fetch_all(user_id)

    for granted_permission in granted:
        if granted_permission == permission:
            return True
        
        if granted_permission == '*':
            return True

        if not granted_permission.endswith('.*'):
            continue

        if permission.startswith(granted_permission[:-2]):
            return True
        
    return False

def is_rejected(permission: str, user_id: int) -> bool:
    permission = permission.lower().removesuffix('.*')
    granted, rejected = fetch_all(user_id)

    for rejected_permission in rejected:
        if rejected_permission == permission:
            return True
        
        if rejected_permission == '*':
            return True

        if not rejected_permission.endswith('.*'):
            continue

        if permission.startswith(rejected_permission[:-2]):
            return True
        
    return False

@caching.ttl_cache(ttl=60*15)
def cached_group_permissions(group_id: int) -> Tuple[List[str], List[str]]:
    return permissions.fetch_group_permissions(group_id)

@caching.ttl_cache(ttl=30)
def cached_user_permissions(user_id: int) -> Tuple[List[str], List[str]]:
    return permissions.fetch_user_permissions(user_id)

@caching.ttl_cache(ttl=60)
def cached_groups(user_id: int) -> List[str]:
    return groups.fetch_user_groups(user_id, True)
