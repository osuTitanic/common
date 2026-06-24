
from .resolver import BeatmapResourceProvider
from .provider_mirror import MirrorResolver
from .provider_storage import StorageResolver
from .provider import BeatmapResources

__all__ = (
    'BeatmapResources',
    'BeatmapResourceProvider',
    'MirrorResolver',
    'StorageResolver',
)
