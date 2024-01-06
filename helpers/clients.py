
from .caching import ttl_cache
from typing import List

import config
import app

@ttl_cache(ttl=3600)
def get_manifest() -> List[dict]:
    response = app.session.requests.get(f'http://osu.{config.DOMAIN_NAME}/clients/manifest.json')

    if not response.ok:
        return []

    return response.json()

def get_client_hashes() -> List[str]:
    return [
        hash['md5']
        for client in get_manifest()
        for hash in client['hashes']
    ]

def is_valid_client_hash(hash: str) -> bool:
    return hash in get_client_hashes()
