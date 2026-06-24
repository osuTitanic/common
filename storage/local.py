
from typing import Generator, List

from ..config import Config
from .base import BaseStorage

import os


class LocalStorage(BaseStorage):
    """Storage backend that stores files on the local filesystem under the configured data path"""

    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def save(self, key: str, content: bytes, bucket: str) -> bool:
        try:
            path = f'{self.config.DATA_PATH}/{bucket}'
            os.makedirs(path, exist_ok=True)
            with open(f'{path}/{key}', 'wb') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f'Failed to save file "{bucket}/{key}": {e}')
            return False

        return True

    def get(self, key: str, bucket: str) -> bytes | None:
        try:
            with open(f'{self.config.DATA_PATH}/{bucket}/{key}', 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to read file "{bucket}/{key}": {e}')
            return None

    def get_iterator(self, key: str, bucket: str, chunk_size: int = 1024 * 64) -> Generator:
        try:
            with open(f'{self.config.DATA_PATH}/{bucket}/{key}', 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to read file "{bucket}/{key}": {e}')
            return None

    def get_size(self, key: str, bucket: str) -> int | None:
        try:
            return os.path.getsize(f'{self.config.DATA_PATH}/{bucket}/{key}')
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to get size of file "{bucket}/{key}": {e}')
            return None

    def remove(self, key: str, bucket: str) -> bool:
        try:
            os.remove(f'{self.config.DATA_PATH}/{bucket}/{key}')
        except Exception as e:
            self.logger.error(f'Failed to remove file "{bucket}/{key}": "{e}"')
            return False

        return True

    def file_exists(self, key: str, folder: str) -> bool:
        return os.path.isfile(f'{self.config.DATA_PATH}/{folder}/{key}')

    def list(self, key: str) -> List[str]:
        return os.listdir(f'{self.config.DATA_PATH}/{key}')

    def get_presigned_url(self, folder: str, key: str, expiration: int = 900) -> str | None:
        return None

    def get_osz_internal_path(self, set_id) -> str | None:
        return f'{self.config.DATA_PATH}/osz/{set_id}'
