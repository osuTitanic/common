
from __future__ import annotations
from typing import List

from ...database.repositories import resources, beatmapsets
from ...database.objects import DBResourceMirror

from requests.adapters import HTTPAdapter
from requests import Session, Response
from urllib3.util.retry import Retry
from urllib.parse import urlparse
from redis import Redis

import logging
import config

class Beatmaps:
    """Wrapper for different beatmap resources, using different API's"""

    def __init__(self, cache: Redis) -> None:
        self.logger = logging.getLogger('beatmap-api')
        self.id_offset = 1000000000

        self.session = Session()
        self.session.headers = {'User-Agent': f'osuTitanic ({config.DOMAIN_NAME})'}
        self.cache = cache

        retries = Retry(
            total=4,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )

        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

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

    def do_safe_request(self, url: str, **kwargs) -> Response:
        try:
            response = self.session.get(url, **kwargs)
        except Exception as e:
            response = Response()
            response.status_code = 500
            self.logger.error(f'Failed to send request to "{url}": {e}')
        finally:
            return response

    def determine_server(self, id: int) -> int:
        return beatmapsets.fetch_download_server_id(id)

    def resolve_mirrors(self, type: int, server: int) -> List[DBResourceMirror]:
        mirror_index = (
            self.cache.get(f'roundrobin:{type}:{server}') or 0
        )

        mirrors = [
            mirror for mirror in resources.fetch_by_type(type, server)
            if not self.check_ratelimit(mirror.url)
        ]

        if not mirrors:
            return []

        mirror_index = int(mirror_index)
        next_index = (mirror_index + 1) % len(mirrors)

        self.cache.set(
            f'roundrobin:{type}:{server}',
            next_index, ex=60
        )

        return mirrors[mirror_index:] + mirrors[:mirror_index]

    def osz(self, set_id: int, no_video: bool = False) -> Response | None:
        self.logger.debug(f'Downloading osz... ({set_id})')

        mirrors = self.resolve_mirrors(
            type=1 if no_video else 0,
            server=self.determine_server(set_id)
        )

        if not mirrors:
            return None

        for mirror in mirrors:
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

        mirrors = self.resolve_mirrors(
            type=5,
            server=self.determine_server(set_id)
        )

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

        mirrors = self.resolve_mirrors(
            type=4 if large else 3,
            server=self.determine_server(set_id)
        )

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
