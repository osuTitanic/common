
from __future__ import annotations

from typing import Generator, Iterator, List, Dict
from botocore.exceptions import ClientError
from botocore.client import BaseClient
from sqlalchemy.orm import Session
from datetime import timedelta
from redis import Redis

from .database.repositories import scores, wrapper
from .helpers.external import Beatmaps
from .database.objects import DBScore
from .helpers import replays

import hashlib
import logging
import config
import boto3
import os
import io

class Storage:
    """This class aims to provide a higher level api for using/managing storage."""

    def __init__(self) -> None:
        self.logger = logging.getLogger('storage')

        self.cache = Redis(
            config.REDIS_HOST,
            config.REDIS_PORT
        )

        self.s3: BaseClient = boto3.client(
            's3',
            endpoint_url=config.S3_BASEURL,
            aws_access_key_id=config.S3_ACCESS_KEY,
            aws_secret_access_key=config.S3_SECRET_KEY
        )

        self.api = Beatmaps(self.cache)

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
    def get_full_replay(self, id: int, session: Session = ...) -> bytes | None:
        score = scores.fetch_by_id(id, session=session)

        if not score:
            return None

        return self.get_full_replay_from_score(score)

    def get_full_replay_from_score(self, score: DBScore) -> bytes | None:
        if not (replay := self.get_replay(score.id)):
            return None

        return replays.serialize_replay(score, replay)

    def get_osz(self, set_id: int, no_video: bool = False) -> Iterator | None:
        if not (osz := self.api.osz(set_id, no_video)):
            return None

        return osz.iter_content(chunk_size=1024 * 64)

    def get_osz_internal(self, set_id: int) -> bytes | None:
        return self.get(f'{set_id}', 'osz')

    def get_osz_iterable(self, set_id: int, chunk_size: int = 1024 * 64) -> Generator:
        return self.get_iterator(f'{set_id}', 'osz', chunk_size)

    def get_osz_size(self, set_id: int) -> int | None:
        return self.get_size(f'{set_id}', 'osz')

    def get_osz2_internal(self, set_id: int) -> bytes | None:
        return self.get(f'{set_id}', 'osz2')

    def get_osz2_iterable(self, set_id: int, chunk_size: int = 1024 * 64) -> Generator:
        return self.get_iterator(f'{set_id}', 'osz2', chunk_size)

    def get_osz2_size(self, set_id: int) -> int | None:
        return self.get_size(f'{set_id}', 'osz2')

    def get_beatmap(self, id: int) -> bytes | None:
        if (osu := self.get_from_cache(f'osu:{id}')):
            return osu

        if not (osu := self.api.osu(id)):
            return None

        self.save_to_cache(
            name=f'osu:{id}',
            content=osu,
            expiry=timedelta(hours=4)
        )

        return osu

    def cache_beatmap(self, id: int) -> None:
        if self.cache.exists(f'osu:{id}'):
            return
        
        if not (osu := self.api.osu(id)):
            return

        self.save_to_cache(
            name=f'osu:{id}',
            content=osu,
            expiry=timedelta(hours=4)
        )

    def get_beatmap_internal(self, id: int) -> bytes | None:
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

    def get_background(self, id: str) -> bytes | None:
        if (image := self.get_from_cache(f'mt:{id}')):
            return image

        if not (id.replace('l', '')).isdigit():
            return None

        set_id = int(id.replace('l', ''))
        large = 'l' in id

        if not (image := self.api.background(set_id, large)):
            return None

        self.save_to_cache(
            name=f'mt:{id}',
            content=image,
            expiry=timedelta(hours=12)
        )

        return image

    def get_background_internal(self, set_id: int) -> bytes | None:
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

        if not (mp3 := self.api.preview(set_id)):
            return None

        self.save_to_cache(
            name=f'mp3:{set_id}',
            content=mp3,
            expiry=timedelta(hours=6)
        )

        return mp3

    def get_mp3_internal(self, set_id: int) -> bytes | None:
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

    def upload_osz(self, set_id: int, content: bytes):
        self.save(f'{set_id}', content, 'osz')

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

    def save(self, key: str, content: bytes, bucket: str) -> bool:
        """Save a file to the specified bucket/directory."""
        if config.S3_ENABLED:
            return self.save_to_s3(content, str(key), bucket)
        else:
            return self.save_to_file(f'{bucket}/{key}', content)

    def get(self, key: str, bucket: str) -> bytes | None:
        """Get a file from the specified bucket/directory."""
        if config.S3_ENABLED:
            return self.get_from_s3(str(key), bucket)
        else:
            return self.get_file_content(f'{bucket}/{key}')

    def get_iterator(self, key: str, bucket: str, chunk_size: int = 1024 * 64) -> Generator:
        """Get a file iterator from the specified bucket/directory."""
        if config.S3_ENABLED:
            return self.get_s3_iterator(str(key), bucket, chunk_size)
        else:
            return self.get_file_iterator(f'{bucket}/{key}', chunk_size)
        
    def get_size(self, key: str, bucket: str) -> int | None:
        if config.S3_ENABLED:
            return self.get_s3_size(str(key), bucket)
        else:
            return self.get_file_size(f'{bucket}/{key}')

    def remove(self, key: str, bucket: str) -> bool:
        """Remove a file from the specified bucket/directory."""
        if config.S3_ENABLED:
            return self.remove_from_s3(str(key), bucket)
        else:
            return self.remove_file(f'{bucket}/{key}')

    def save_to_cache(self, name: str, content: bytes, expiry=timedelta(days=1), override=True) -> bool:
        if len(content) > 40_000_000: return True
        return self.cache.set(f'{name}', content, expiry, nx=(not override))

    def get_from_cache(self, name: str) -> bytes | None:
        return self.cache.get(f'{name}')

    def remove_from_cache(self, name: str) -> bool:
        return self.cache.delete(f'{name}')

    def save_to_file(self, filepath: str, content: bytes) -> bool:
        try:
            with open(f'{config.DATA_PATH}/{filepath}', 'wb') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f'Failed to save file "{filepath}": {e}')
            return False

        return True

    def save_to_s3(self, content: bytes, key: str, bucket: str) -> bool:
        try:
            self.s3.upload_fileobj(
                io.BytesIO(content),
                bucket,
                key
            )
        except Exception as e:
            self.logger.error(f'Failed to upload "{key}" to s3: "{e}"')
            return False

        return True

    def get_file_content(self, filepath: str) -> bytes | None:
        try:
            with open(f'{config.DATA_PATH}/{filepath}', 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to read file "{filepath}": {e}')
            return None

    def get_file_iterator(self, filepath: str, chunk_size: int = 1024 * 64) -> Generator:
        try:
            with open(f'{config.DATA_PATH}/{filepath}', 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to read file "{filepath}": {e}')
            return None

    def get_file_size(self, filepath: str) -> int | None:
        try:
            return os.path.getsize(f'{config.DATA_PATH}/{filepath}')
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to get size of file "{filepath}": {e}')
            return None

    def get_from_s3(self, key: str, bucket: str) -> bytes | None:
        buffer = io.BytesIO()

        try:
            self.s3.download_fileobj(
                bucket,
                key,
                buffer
            )
        except ClientError:
            # Most likely not found
            return None
        except Exception as e:
            self.logger.error(f'Failed to download "{key}" from s3: "{e}"')
            return None

        return buffer.getvalue()

    def get_s3_iterator(self, key: str, bucket: str, chunk_size: int = 1024 * 64) -> Generator:
        buffer = io.BytesIO()

        try:
            self.s3.download_fileobj(
                bucket,
                key,
                buffer
            )
        except ClientError:
            # Most likely not found
            return
        except Exception as e:
            self.logger.error(f'Failed to download "{key}" from s3: "{e}"')
            return

        buffer.seek(0)

        while chunk := buffer.read(chunk_size):
            yield chunk

    def get_s3_size(self, key: str, bucket: str) -> int | None:
        try:
            response = self.s3.head_object(Bucket=bucket, Key=key)
            return response['ContentLength']
        except ClientError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to get size of "{key}" from s3: "{e}"')
            return None

    def remove_from_s3(self, key: str, bucket: str) -> bool:
        try:
            self.s3.delete_object(
                Bucket=bucket,
                Key=key
            )
        except Exception as e:
            self.logger.error(f'Failed to remove "{key}" from {bucket}: "{e}"')
            return False

        return True

    def remove_file(self, filepath: str) -> bool:
        try:
            os.remove(f'{config.DATA_PATH}/{filepath}')
        except Exception as e:
            self.logger.error(f'Failed to file "{filepath}": "{e}"')
            return False

        return True

    def file_exists(self, key: str, bucket: str) -> bool:
        """Check if a file exists in the specified bucket/directory."""
        if not config.S3_ENABLED:
            return os.path.isfile(f'{config.DATA_PATH}/{bucket}/{key}')

        try:
            self.s3.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

    def list(self, key: str) -> List[str]:
        """Get a list of filenames from the specified bucket/directory."""
        if not config.S3_ENABLED:
            return self.list_directory(key)
        else:
            return self.list_bucket(key)

    def list_directory(self, dir: str) -> List[str]:
        return os.listdir(f'{config.DATA_PATH}/{dir}')

    def list_bucket(self, bucket: str) -> List[str]:
        return [object['Key'] for object in self.s3.list_objects(Bucket=bucket)['Contents']]

    def get_file_hashes(self, key: str) -> Dict[str, str]:
        """Get a dictionary of file hashes from the specified bucket/directory."""
        if config.S3_ENABLED:
            return self.get_file_hashes_s3(key)
        else:
            return self.get_file_hashes_local(key)

    def get_file_hashes_s3(self, bucket: str) -> Dict[str, str]:
        if not config.S3_ENABLED:
            return {}

        try:
            return {
                object['Key']: object['ETag'].replace('"', '')
                for object in self.s3.list_objects(Bucket=bucket)['Contents']
            }
        except Exception as e:
            self.logger.error(f'Failed to get etags: {e}')
            return {}

    def get_file_hashes_local(self, directory: str) -> Dict[str, str]:
        if config.S3_ENABLED:
            return {}

        try:
            file_hashes = {}

            for filename in os.listdir(f'{config.DATA_PATH}/{directory}'):
                try:
                    with open(f'{config.DATA_PATH}/{directory}/{filename}', 'rb') as file:
                        file_content = file.read()
                        file_hash = hashlib.md5(file_content).hexdigest()
                        file_hashes[filename] = file_hash
                except Exception as e:
                    self.logger.error(
                        f'Failed to read file "{filename}": {e}',
                        exc_info=e
                    )
        except Exception as e:
            self.logger.error(
                f'Failed to list files in directory "{directory}": {e}',
                exc_info=e
            )

        return file_hashes

    def get_presigned_url(self, bucket: str, key: str, expiration: int = 900) -> str | None:
        """Generate a presigned url for the specified bucket & key."""
        if not config.S3_ENABLED:
            return None

        try:
            return self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket,
                    'Key': str(key)
                },
                ExpiresIn=expiration
            )
        except ClientError as e:
            self.logger.error(f'Failed to generate presigned url: {e}')
            return None
