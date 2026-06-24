
from ..config import Config
from .local import LocalStorage
from .base import BaseStorage
from .s3 import S3Storage

def Storage(config: Config) -> BaseStorage:
    if config.S3_ENABLED:
        return S3Storage(config)

    return LocalStorage(config)

__all__ = ('Storage', 'BaseStorage', 'LocalStorage', 'S3Storage')
