
from ...storage.base import BaseStorage
from ...database.repositories import beatmapsets
from .resolver import BeatmapResourceProvider
from .provider_mirror import MirrorResolver
from .provider_storage import StorageResolver

from datetime import timedelta
from typing import Iterator
from redis import Redis

import logging

class BeatmapResources:
    """Wrapper for different beatmap resources, using different API's"""

    def __init__(self, storage: BaseStorage, cache: Redis) -> None:
        self.logger = logging.getLogger('beatmap-resources')
        self.storage = storage
        self.cache = cache

        self.mirror_resolver = MirrorResolver(cache)
        self.storage_resolver = StorageResolver(storage)

        # Compatibility handle for callers that need the raw mirror response
        self.api = self.mirror_resolver

        self.resolvers: dict[int, BeatmapResourceProvider] = {
            0: self.mirror_resolver,
            1: self.storage_resolver,
        }
        self.fallback = self.mirror_resolver

    def osz(self, set_id: int, no_video: bool = False) -> Iterator | None:
        """Stream an .osz archive for the given set"""
        return self.resolver_for_set(set_id).osz(set_id, no_video)

    def osu(self, beatmap_id: int) -> bytes | None:
        """Return a beatmap (.osu) file"""
        if (osu := self.cache_get(f'osu:{beatmap_id}')):
            return osu

        if not (osu := self.resolver_for_beatmap(beatmap_id).osu(beatmap_id)):
            return None

        self.cache_set(f'osu:{beatmap_id}', osu, timedelta(hours=4))
        return osu

    def cache_beatmap(self, beatmap_id: int) -> None:
        """Populate the .osu cache for a beatmap if not already cached"""
        if self.cache.exists(f'osu:{beatmap_id}'):
            return

        if not (osu := self.resolver_for_beatmap(beatmap_id).osu(beatmap_id)):
            return

        self.cache_set(f'osu:{beatmap_id}', osu, timedelta(hours=4))

    def preview(self, set_id: int) -> bytes | None:
        """Return the .mp3 preview for a set"""
        if (mp3 := self.cache_get(f'mp3:{set_id}')):
            return mp3

        if not (mp3 := self.resolver_for_set(set_id).preview(set_id)):
            return None

        self.cache_set(f'mp3:{set_id}', mp3, timedelta(hours=6))
        return mp3

    def background(self, set_id: int, large: bool = False) -> bytes | None:
        """Return the thumbnail image for a set"""
        key = f'mt:{set_id}l' if large else f'mt:{set_id}'

        if (image := self.cache_get(key)):
            return image

        if not (image := self.resolver_for_set(set_id).background(set_id, large)):
            return None

        self.cache_set(key, image, timedelta(hours=12))
        return image

    def resolver_for_server(self, server: int) -> BeatmapResourceProvider:
        return self.resolvers.get(server, self.fallback)

    def resolver_for_set(self, set_id: int) -> BeatmapResourceProvider:
        return self.resolver_for_server(
            beatmapsets.fetch_download_server_id(set_id)
        )

    def resolver_for_beatmap(self, beatmap_id: int) -> BeatmapResourceProvider:
        return self.resolver_for_server(
            beatmapsets.fetch_download_server_by_beatmap(beatmap_id)
        )

    def cache_get(self, name: str) -> bytes | None:
        return self.cache.get(name)

    def cache_set(self, name: str, content: bytes, expiry: timedelta) -> None:
        if len(content) > 40_000_000: # 40MB
            return
        self.cache.set(name, content, expiry)
