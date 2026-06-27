
from typing import Generator, List, Any, IO
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from datetime import timedelta
from redis import Redis

from ..database.repositories import scores, wrapper
from ..database.objects import DBScore
from ..helpers import replays, cloudflare
from ..config import Config

import logging


class BaseStorage(ABC):
    """Base class for storage backends"""

    def __init__(self, config: Config) -> None:
        self.logger = logging.getLogger('storage')
        self.config = config
        self.cache = Redis(
            self.config.REDIS_HOST,
            self.config.REDIS_PORT
        )

    @abstractmethod
    def save(self, key: str, content: bytes, bucket: str) -> bool: ...

    @abstractmethod
    def get(self, key: str, bucket: str) -> bytes | None: ...

    @abstractmethod
    def get_iterator(self, key: str, bucket: str, chunk_size: int = 1024 * 64) -> Generator: ...

    @abstractmethod
    def get_io(self, key: str, bucket: str) -> IO[bytes] | None: ...

    @abstractmethod
    def get_size(self, key: str, bucket: str) -> int | None: ...

    @abstractmethod
    def remove(self, key: str, bucket: str) -> bool: ...

    @abstractmethod
    def file_exists(self, key: str, folder: str) -> bool: ...

    @abstractmethod
    def list(self, key: str) -> List[str]: ...

    @abstractmethod
    def get_presigned_url(self, folder: str, key: str, expiration: int = 900) -> str | None: ...

    def get_osz_internal_path(self, set_id: int) -> str | None:
        """Filesystem path to an .osz file"""
        return None

    def get_from_cache(self, name: str) -> Any | None:
        return self.cache.get(f'{name}')

    def save_to_cache(self, name: str, content: bytes, expiry=timedelta(days=1), override=True) -> bool:
        if len(content) > 40_000_000:
            return True
        return bool(self.cache.set(f'{name}', content, expiry, nx=(not override)))

    def remove_from_cache(self, name: str) -> bool:
        return bool(self.cache.delete(f'{name}'))

    def get_avatar(self, id: str) -> bytes | None:
        if (image := self.get_from_cache(f'avatar:{id}')):
            return image

        image = self.get(id, 'avatars')

        if not image:
            return None

        self.save_to_cache(
            name=f'avatar:{id}',
            content=image,
            expiry=timedelta(days=1)
        )

        return image

    def get_screenshot(self, id: int) -> bytes | None:
        if (image := self.get_from_cache(f'screenshots:{id}')):
            return image

        image = self.get(f'{id}', 'screenshots')

        if not image:
            return None

        self.save_to_cache(
            name=f'screenshots:{id}',
            content=image,
            expiry=timedelta(hours=4)
        )

        return image

    def get_replay(self, id: int) -> bytes | None:
        if (replay := self.get_from_cache(f'osr:{id}')):
            return replay

        replay = self.get(f'{id}', 'replays')

        if not replay:
            return None

        self.save_to_cache(
            name=f'osr:{id}',
            content=replay,
            expiry=timedelta(hours=1)
        )

        return replay

    @wrapper.session_wrapper
    def get_full_replay(self, id: int, session: Session = wrapper.SessionProvider) -> bytes | None:
        score = scores.fetch_by_id(id, session=session)

        if not score:
            return None

        return self.get_full_replay_from_score(score)

    def get_full_replay_from_score(self, score: DBScore) -> bytes | None:
        if not (replay := self.get_replay(score.id)):
            return None

        return replays.serialize_replay(score, replay)

    def get_osz(self, set_id: int) -> bytes | None:
        return self.get(f'{set_id}', 'osz')

    def get_osz_iterable(self, set_id: int, chunk_size: int = 1024 * 64) -> Generator:
        return self.get_iterator(f'{set_id}', 'osz', chunk_size)

    def get_osz_io(self, set_id: int) -> IO[bytes] | None:
        return self.get_io(f'{set_id}', 'osz')

    def get_osz_size(self, set_id: int) -> int | None:
        return self.get_size(f'{set_id}', 'osz')

    def get_osz2(self, set_id: int) -> bytes | None:
        return self.get(f'{set_id}', 'osz2')

    def get_osz2_iterable(self, set_id: int, chunk_size: int = 1024 * 64) -> Generator:
        return self.get_iterator(f'{set_id}', 'osz2', chunk_size)

    def get_osz2_io(self, set_id: int) -> IO[bytes] | None:
        return self.get_io(f'{set_id}', 'osz2')

    def get_osz2_size(self, set_id: int) -> int | None:
        return self.get_size(f'{set_id}', 'osz2')

    def get_beatmap(self, id: int) -> bytes | None:
        if (osu := self.get_from_cache(f'osu:{id}')):
            return osu

        osu = self.get(f'{id}', 'beatmaps')

        if not osu:
            return None

        self.save_to_cache(
            name=f'osu:{id}',
            content=osu,
            expiry=timedelta(hours=4)
        )

        return osu

    def get_background(self, set_id: int) -> bytes | None:
        if (image := self.get_from_cache(f'mt:{set_id}l')):
            return image

        image = self.get(f'{set_id}', 'thumbnails')

        if not image:
            return None

        self.save_to_cache(
            name=f'mt:{set_id}l',
            content=image,
            expiry=timedelta(hours=12)
        )

        return image

    def get_mp3(self, set_id: int) -> bytes | None:
        if (mp3 := self.get_from_cache(f'mp3:{set_id}')):
            return mp3

        mp3 = self.get(f'{set_id}', 'audio')

        if not mp3:
            return None

        self.save_to_cache(
            name=f'mp3:{set_id}',
            content=mp3,
            expiry=timedelta(hours=6)
        )

        return mp3

    def get_release_file(self, filename: str) -> bytes | None:
        return self.get(filename, 'release')

    def get_release_file_iterator(self, filename: str, chunk_size: int = 1024 * 64) -> Generator:
        return self.get_iterator(filename, 'release', chunk_size)

    def get_release_file_size(self, filename: str) -> int | None:
        return self.get_size(filename, 'release')

    def purge_osz_cache(self, set_id: int) -> None:
        try:
            cloudflare.purge_beatmapset(set_id)
        except Exception as error:
            self.logger.warning(f'Failed to purge osz cache for "{set_id}": {error}')

    def upload_osz(self, set_id: int, content: bytes):
        self.save(f'{set_id}', content, 'osz')
        self.purge_osz_cache(set_id)

    def upload_osz2(self, set_id: int, content: bytes):
        self.save(f'{set_id}', content, 'osz2')

    def upload_avatar(self, id: int, content: bytes):
        self.remove_avatar(id)
        self.save(f'{id}', content, 'avatars')
        self.save_to_cache(
            name=f'avatar:{id}',
            content=content,
            expiry=timedelta(hours=12)
        )

    def upload_screenshot(self, id: int, content: bytes):
        self.save(f'{id}', content, 'screenshots')
        self.save_to_cache(
            name=f'screenshots:{id}',
            content=content,
            expiry=timedelta(hours=2)
        )

    def upload_replay(self, id: int, content: bytes):
        self.save(f'{id}', content, 'replays')
        self.save_to_cache(
            name=f'osr:{id}',
            content=content,
            expiry=timedelta(hours=6)
        )

    def upload_beatmap_file(self, id: int, content: bytes):
        self.save(f'{id}', content, 'beatmaps')
        self.save_to_cache(
            name=f'osu:{id}',
            content=content,
            expiry=timedelta(hours=4)
        )

    def upload_background(self, set_id: int, content: bytes):
        self.remove_from_cache(f'mt:{set_id}')
        self.remove_from_cache(f'mt:{set_id}l')
        self.save(f'{set_id}', content, 'thumbnails')
        self.save_to_cache(
            name=f'mt:{set_id}l',
            content=content,
            expiry=timedelta(hours=12)
        )

    def upload_mp3(self, set_id: int, content: bytes):
        self.save(f'{set_id}', content, 'audio')
        self.save_to_cache(
            name=f'mp3:{set_id}',
            content=content,
            expiry=timedelta(hours=6)
        )

    def cache_replay(self, id: int, content: bytes, time=timedelta(days=1)):
        self.save_to_cache(
            name=f'osr:{id}',
            content=content,
            expiry=time
        )

    def remove_replay(self, id: int):
        self.logger.debug(f'Removing replay with id "{id}"...')
        self.remove_from_cache(f'osr:{id}')
        self.remove(f'{id}', 'replays')

    def remove_beatmap_file(self, beatmap_id: int):
        self.logger.debug(f'Removing beatmap file with id "{beatmap_id}"...')
        self.remove_from_cache(f'osu:{beatmap_id}')
        self.remove(f'{beatmap_id}', 'beatmaps')

    def remove_osz(self, set_id: int):
        self.logger.debug(f'Removing osz with id "{set_id}"...')
        self.remove(f'{set_id}', 'osz')
        self.purge_osz_cache(set_id)

    def remove_osz2(self, set_id: int):
        self.logger.debug(f'Removing osz2 with id "{set_id}"...')
        self.remove(f'{set_id}', 'osz2')

    def remove_background(self, set_id: int):
        self.logger.debug(f'Removing background with id "{set_id}"...')
        self.remove_from_cache(f'mt:{set_id}l')
        self.remove(f'{set_id}', 'thumbnails')

    def remove_mp3(self, set_id: int):
        self.logger.debug(f'Removing mp3 with id "{set_id}"...')
        self.remove_from_cache(f'mp3:{set_id}')
        self.remove(f'{set_id}', 'audio')

    def remove_avatar(self, id: int):
        self.logger.debug(f'Removing avatar with id "{id}"...')
        self.remove_from_cache(f'avatar:{id}')
        self.remove(f'{id}', 'avatars')

        for size in (25, 128, 256):
            self.remove_from_cache(f'avatar:{id}:{size}')
