
from ...database.repositories import resources

from requests import Session, Response
from typing import Optional

import logging

class Beatmaps:
    """Wrapper for different beatmap resources, using different API's"""

    def __init__(self) -> None:
        self.logger = logging.getLogger('beatmap-api')

        self.session = Session()
        self.session.headers = {
            'User-Agent': 'osuTitanic/titanic'
        }

    def log_error(self, url: str, status_code: int) -> None:
        self.logger.error(f'Error while sending request to "{url}" ({status_code})')

    def osz(self, set_id: int, no_video: bool = False, server: int = 0) -> Optional[Response]:
        self.logger.debug(f'Downloading osz... ({set_id})')

        mirrors = resources.fetch_by_type(
            type=(1 if no_video else 0),
            server=server
        )

        for mirror in mirrors:
            response = self.session.get(
                mirror.url.format(set_id),
                stream=True
            )

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            # NOTE: Some mirrors like osu.direct always responds with status code
            #       200, even on errors. So here is a little workaround for that

            if 'application/json' in response.headers['Content-Type']:
                self.log_error(response.url, response.json()['code'])
                continue

            return response
    
    def osu(self, beatmap_id: int, server: int = 0) -> Optional[bytes]:
        self.logger.debug(f'Downloading beatmap... ({beatmap_id})')

        mirrors = resources.fetch_by_type(
            type=2,
            server=server
        )

        for mirror in mirrors:
            response = self.session.get(mirror.url.format(beatmap_id))

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            if 'application/json' in response.headers['Content-Type']:
                self.log_error(response.url, response.json()['code'])
                continue

            if not response.content:
                continue

            return response.content

    def preview(self, set_id: int, server: int = 0) -> Optional[bytes]:
        self.logger.debug(f'Downloading preview... ({set_id})')

        mirrors = resources.fetch_by_type(
            type=5,
            server=server
        )

        for mirror in mirrors:
            response = self.session.get(mirror.url.format(set_id))

            if not response.ok:
                self.log_error(response.url, response.status_code)
                continue

            return response.content

    def background(self, set_id: int, large=False, server: int = 0) -> Optional[bytes]:
        self.logger.debug(f'Downloading background... ({set_id})')

        mirrors = resources.fetch_by_type(
            type=(4 if large else 3),
            server=server
        )

        for mirror in mirrors:
            response = self.session.get(mirror.url.format(set_id))

            if not response.ok:
                if response.status_code != 404:
                    # Prevent flooding the console with 404 errors lol
                    self.log_error(response.url, response.status_code)
                continue

            return response.content
