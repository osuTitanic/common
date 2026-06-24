
from typing import Iterator
from abc import ABC, abstractmethod

class BeatmapResourceProvider(ABC):
    """Resolves beatmap resources from a single source"""

    @abstractmethod
    def osz(self, set_id: int, no_video: bool = False) -> Iterator | None:
        """Stream an .osz archive for the given beatmapset"""
        ...

    @abstractmethod
    def osu(self, beatmap_id: int) -> bytes | None:
        """Return a beatmap (.osu) file for the given beatmap"""
        ...

    @abstractmethod
    def preview(self, set_id: int) -> bytes | None:
        """Return the audio preview for a beatmapset"""
        ...

    @abstractmethod
    def background(self, set_id: int, large: bool = False) -> bytes | None:
        """Return the thumbnail image for a beatmapset"""
        ...
