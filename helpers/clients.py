

from .caching import ttl_cache
from .. import officer

from typing import List

import config
import app

@ttl_cache(ttl=3600)
def get_manifest() -> List[dict]:
    app.session.logger.debug('Fetching client manifest...')

    try:
        response = app.session.requests.get(
            f'http://osu.{config.DOMAIN_NAME}/clients/manifest.json'
        )

        if not response.ok:
            return []

        clients = response.json()

        app.session.logger.debug(
            'Client manifest fetched successfully. '
            f'({len(clients)} clients)'
        )

        return clients
    except Exception as e:
        app.session.logger.error(
            f'Failed to fetch client manifest: {e}',
            exc_info=e
        )

    return []

def get_client_hashes() -> List[str]:
    return [
        hash['md5']
        for client in get_manifest()
        for hash in client['hashes']
    ]

def is_valid_client_hash(hash: str) -> bool:
    if not (hashes := get_client_hashes()):
        officer.call(
            f'Failed to get client hashes, assuming valid. ({hash})'
        )
        return True

    return hash in hashes
