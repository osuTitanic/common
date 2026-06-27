
from ..config import config_instance as config
from typing import Iterable, Iterable, List

import requests
import logging

logger = logging.getLogger('cloudflare')
session = requests.Session()
session.headers.update({'User-Agent': f'osuTitanic/stern ({config.DOMAIN_NAME})'})

# Cloudflare accepts at most 30 urls per request
MAX_URLS_PER_REQUEST = 30

def purge_enabled() -> bool:
    return bool(
        config.CLOUDFLARE_PURGE_ENABLED and
        config.CLOUDFLARE_ZONE_ID and
        config.CLOUDFLARE_API_TOKEN
    )

def purge_urls(urls: Iterable[str]) -> bool:
    if not purge_enabled():
        return False

    # Deduplicate & remove empty urls
    urls = [url for url in dict.fromkeys(urls) if url]

    if not urls:
        return False

    endpoint = f'https://api.cloudflare.com/client/v4/zones/{config.CLOUDFLARE_ZONE_ID}/purge_cache'
    headers = {'Authorization': f'Bearer {config.CLOUDFLARE_API_TOKEN}'}
    success = True

    for batch in chunks(urls, MAX_URLS_PER_REQUEST):
        try:
            response = session.post(
                endpoint,
                headers=headers,
                json={'files': batch},
                timeout=10
            )
            response.raise_for_status()
        except Exception as error:
            logger.warning(f'Failed to purge cloudflare cache: {error}')
            success = False
            continue

        logger.debug(f'Purged {len(batch)} url(s) from cloudflare cache')

    return success

def purge_beatmapset(set_id: int) -> bool:
    if not purge_enabled():
        return False

    return purge_urls(osz_urls(set_id))

def osz_urls(set_id: int) -> List[str]:
    if config.CLOUDFLARE_PURGE_OSZ_URLS:
        return [
            template.format(id=set_id)
            for template in config.CLOUDFLARE_PURGE_OSZ_URLS
        ]

    # Fall back to the default download urls
    base = config.OSU_BASEURL.rstrip('/')

    return [
        f'{base}/d/{set_id}',
        f'{base}/d/{set_id}n',
        f'{base}/beatmapsets/download/{set_id}',
        f'{base}/beatmapsets/download/{set_id}?novideo=True',
    ]

def chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for index in range(0, len(items), size):
        yield items[index:index + size]
