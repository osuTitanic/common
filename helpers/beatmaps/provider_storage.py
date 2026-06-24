
from typing import Iterator, Tuple
from PIL import Image

from .resolver import BeatmapResourceProvider
from ..streaming import NoVideoZipIterator
from ...storage.base import BaseStorage

import logging
import io

class StorageResolver(BeatmapResourceProvider):
    """Resolves beatmap resources directly from our own storage backend"""

    def __init__(self, storage: BaseStorage) -> None:
        self.logger = logging.getLogger('beatmap-storage')
        self.storage = storage

    def osz(self, set_id: int, no_video: bool = False) -> Tuple[Iterator | None, int]:
        self.logger.debug(f'Reading osz from storage... ({set_id})')

        if not self.storage.file_exists(f'{set_id}', 'osz'):
            return None, 0

        if not no_video:
            return self.storage.get_osz_iterable(set_id), self.storage.get_osz_size(set_id) or 0

        if not (osz := self.storage.get_osz_internal(set_id)):
            return None, 0

        return NoVideoZipIterator(io.BytesIO(osz)), len(osz)

    def osu(self, beatmap_id: int) -> bytes | None:
        self.logger.debug(f'Reading beatmap from storage... ({beatmap_id})')
        return self.storage.get_beatmap_internal(beatmap_id)

    def preview(self, set_id: int) -> bytes | None:
        self.logger.debug(f'Reading preview from storage... ({set_id})')
        return self.storage.get_mp3_internal(set_id)

    def background(self, set_id: int, large: bool = False) -> bytes | None:
        self.logger.debug(f'Reading background from storage... ({set_id}, large={large})')

        if not (image := self.storage.get_background_internal(set_id)):
            return None

        # We only keep a single (large) thumbnail per set in storage
        if large:
            return image

        return self.resize_thumbnail(image)

    def resize_thumbnail(self, image: bytes) -> bytes:
        try:
            buffer = io.BytesIO()
            resized = Image.open(io.BytesIO(image)).resize(
                (80, 60)
            )
            resized.save(buffer, format='JPEG')
            return buffer.getvalue()
        except Exception as e:
            self.logger.warning(f'Failed to resize thumbnail, serving original anyway: {e}')
            return image
