
from __future__ import annotations

from ...database.repositories import resources

from requests import Session, Response
from urllib.parse import urlparse
from redis import Redis

import logging
import config
import time

class Beatmaps:
    """Wrapper for different beatmap resources, using different API's"""

    def __init__(self, cache: Redis) -> None:
        self.logger = logging.getLogger('beatmap-api')

        self.session = Session()
        self.session.headers = {'User-Agent': 'osuTitanic/titanic'}
        self.cache = cache

    def check_ratelimit(self, url: str) -> bool:
        domain = urlparse(self.format_mirror_url(url, 0)).netloc
        return self.cache.exists(f'ratelimit:{domain}')

    def set_ratelimit(self, url: str, ex: int = 120) -> None:
        domain = urlparse(self.format_mirror_url(url, 0)).netloc
        self.cache.set(f'ratelimit:{domain}', 1, ex=ex)
        self.logger.warning(f'Rate limited on "{domain}", will expire in {ex} seconds')

    def log_error(self, url: str, status_code: int) -> None:
        if status_code == 404:
            self.logger.debug(f'Failed to find resource "{url}" ({status_code})')
            return

        self.logger.error(f'Error while sending request to "{url}" ({status_code})')

    def do_safe_request(self, url: str, **kwargs) -> Response | None:
        try:
            response = self.session.get(url, **kwargs)
        except Exception as e:
            response = Response()
            response.status_code = 500
            self.logger.error(f'Failed to send request to "{url}": {e}')
        finally:
            return response

    def osz(self, set_id: int, no_video: bool = False) -> Response | None:
        self.logger.debug(f'Downloading osz... ({set_id})')

        mirrors = resources.fetch_by_type_all(1 if no_video else 0)

        for mirror in mirrors:
            if self.check_ratelimit(mirror.url):
                continue

            response = self.do_safe_request(
                self.format_mirror_url(mirror.url, set_id),
                stream=True
            )

            if response.status_code == 429:
                # Rate limited, try again later
                self.set_ratelimit(mirror.url)
                continue

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            if 'application/json' in response.headers.get('Content-Type', ''):
                self.log_error(response.url, response.json().get('code', 500))
                continue

            return response
    
    def osu(self, beatmap_id: int) -> bytes | None:
        self.logger.debug(f'Downloading beatmap... ({beatmap_id})')

        mirrors = resources.fetch_by_type_all(2)

        for mirror in mirrors:
            if self.check_ratelimit(mirror.url):
                continue

            response = self.do_safe_request(
                self.format_mirror_url(mirror.url, beatmap_id)
            )

            if response.status_code == 429:
                # Rate limited, try again later
                self.set_ratelimit(mirror.url)
                continue

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            if 'application/json' in response.headers.get('Content-Type', ''):
                self.log_error(response.url, response.json()['code'])
                continue

            if not response.content:
                continue

            return response.content

    def preview(self, set_id: int) -> bytes | None:
        self.logger.debug(f'Downloading preview... ({set_id})')

        mirrors = resources.fetch_by_type_all(5)

        for mirror in mirrors:
            if self.check_ratelimit(mirror.url):
                continue

            response = self.do_safe_request(
                self.format_mirror_url(mirror.url, set_id)
            )

            if response.status_code == 429:
                # Rate limited, try again later
                self.set_ratelimit(mirror.url)
                continue

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            return response.content

    def background(self, set_id: int, large=False) -> bytes | None:
        self.logger.debug(f'Downloading background... ({set_id})')

        mirrors = resources.fetch_by_type_all(4 if large else 3)

        for mirror in mirrors:
            if self.check_ratelimit(mirror.url):
                continue

            response = self.do_safe_request(
                self.format_mirror_url(mirror.url, set_id)
            )

            if response.status_code == 429:
                # Rate limited, try again later
                self.set_ratelimit(mirror.url)
                continue

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            return response.content

    @staticmethod
    def format_mirror_url(url: str, id: int) -> str:
        if url.startswith('/'):
            # Fix for local domains (e.g. /beatmapsets/{}/download)
            url = f'http://{config.DOMAIN_NAME}{url}'

        # Insert the id into the url
        return url.format(id)
