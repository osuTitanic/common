
from __future__ import annotations

from boto3_type_annotations.s3 import Client
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Dict
from redis import Redis

from .database.repositories import scores, wrapper
from .helpers.external import Beatmaps
from .streams import StreamOut
from .helpers import replays
from .constants import Mods

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

        self.s3: Client = boto3.client(
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
            return

        self.save_to_cache(
            name=f'avatar:{id}',
            content=image,
            expiry=timedelta(days=1)
        )

        return image

    def get_screenshot(self, id: int) -> bytes | None:
        if (image := self.get_from_cache(f'screenshots:{id}')):
            return image

        image = self.get(id, 'screenshots')

        if not image:
            return

        self.save_to_cache(
            name=f'screenshots:{id}',
            content=image,
            expiry=timedelta(hours=4)
        )

        return image

    def get_replay(self, id: int) -> bytes | None:
        if (replay := self.get_from_cache(f'osr:{id}')):
            return replay

        replay = self.get(id, 'replays')

        if not replay:
            return

        self.save_to_cache(
            name=f'osr:{id}',
            content=replay,
            expiry=timedelta(hours=1)
        )

        return replay

    @wrapper.session_wrapper
    def get_full_replay(self, id: int, session: Session = ...) -> bytes | None:
        if not (replay := self.get_replay(id)):
            return

        score = scores.fetch_by_id(id, session=session)

        if not score:
            return

        mods = Mods(score.mods)

        if Mods.Nightcore in mods and Mods.DoubleTime not in mods:
            # NC requires DT to be present
            score.mods |= Mods.DoubleTime.value

        stream = StreamOut()
        stream.u8(score.mode)
        stream.s32(score.client_version)
        stream.string(score.beatmap.md5)
        stream.string(score.user.name)
        stream.string(replays.compute_offline_score_checksum(score))
        stream.u16(score.n300)
        stream.u16(score.n100)
        stream.u16(score.n50)
        stream.u16(score.nGeki)
        stream.u16(score.nKatu)
        stream.u16(score.nMiss)
        stream.s32(score.total_score)
        stream.u16(score.max_combo)
        stream.bool(score.perfect)
        stream.s32(score.mods)
        stream.string('') # TODO: HP Graph
        stream.s64(replays.get_ticks(score.submitted_at))
        stream.s32(len(replay))
        stream.write(replay)
        stream.s32(score.id)
        return stream.get()

    def get_osz_internal(self, set_id: int) -> bytes | None:
        return self.get(set_id, 'osz')

    def get_osz2_internal(self, set_id: int) -> bytes | None:
        return self.get(set_id, 'osz2')

    def get_osz(self, set_id: int, no_video: bool = False) -> bytes | None:
        if not (osz := self.api.osz(set_id, no_video)):
            return

        return osz.content

    def get_beatmap(self, id: int) -> bytes | None:
        if (osu := self.get_from_cache(f'osu:{id}')):
            return osu

        if not (osu := self.api.osu(id)):
            return

        self.save_to_cache(
            name=f'osu:{id}',
            content=osu,
            expiry=timedelta(days=1)
        )

        return osu

    def get_beatmap_internal(self, id: int) -> bytes | None:
        if (osu := self.get_from_cache(f'osu:{id}')):
            return osu

        osu = self.get(id, 'beatmaps')

        if not osu:
            return

        self.save_to_cache(
            name=f'osu:{id}',
            content=osu,
            expiry=timedelta(days=1)
        )

        return osu

    def get_background(self, id: str) -> bytes | None:
        if (image := self.get_from_cache(f'mt:{id}')):
            return image

        if not (id.replace('l', '')).isdigit():
            return

        set_id = int(id.replace('l', ''))
        large = 'l' in id

        if not (image := self.api.background(set_id, large)):
            return

        self.save_to_cache(
            name=f'mt:{id}',
            content=image,
            expiry=timedelta(days=1)
        )

        return image

    def get_background_internal(self, set_id: int) -> bytes | None:
        if (image := self.get_from_cache(f'mt:{set_id}l')):
            return image

        image = self.get(set_id, 'thumbnails')

        if not image:
            return

        self.save_to_cache(
            name=f'mt:{set_id}l',
            content=image,
            expiry=timedelta(days=1)
        )

        return image

    def get_mp3(self, set_id: int) -> bytes | None:
        if (mp3 := self.get_from_cache(f'mp3:{set_id}')):
            return mp3

        if not (mp3 := self.api.preview(set_id)):
            return

        self.save_to_cache(
            name=f'mp3:{set_id}',
            content=mp3,
            expiry=timedelta(days=1)
        )

        return mp3

    def get_mp3_internal(self, set_id: int) -> bytes | None:
        if (mp3 := self.get_from_cache(f'mp3:{set_id}')):
            return mp3

        mp3 = self.get(set_id, 'audio')

        if not mp3:
            return

        self.save_to_cache(
            name=f'mp3:{set_id}',
            content=mp3,
            expiry=timedelta(days=1)
        )

        return mp3

    def get_release_file(self, filename: str) -> bytes | None:
        return self.get(filename, 'release')

    def upload_osz(self, set_id: int, content: bytes):
        self.save(set_id, content, 'osz')
        self.save_to_cache(
            name=f'osz:{set_id}',
            content=content,
            expiry=timedelta(hours=12)
        )

    def upload_osz2(self, set_id: int, content: bytes):
        self.save(set_id, content, 'osz2')
        self.save_to_cache(
            name=f'osz2:{set_id}',
            content=content,
            expiry=timedelta(hours=12)
        )

    def upload_avatar(self, id: int, content: bytes):
        self.remove_avatar(id)
        self.save(id, content, 'avatars')
        self.save_to_cache(
            name=f'avatar:{id}',
            content=content,
            expiry=timedelta(days=1)
        )

    def upload_screenshot(self, id: int, content: bytes):
        self.save(id, content, 'screenshots')
        self.save_to_cache(
            name=f'screenshots:{id}',
            content=content,
            expiry=timedelta(hours=4)
        )
    
    def upload_replay(self, id: int, content: bytes):
        self.save(id, content, 'replays')
        self.save_to_cache(
            name=f'osr:{id}',
            content=content,
            expiry=timedelta(days=1)
        )

    def upload_beatmap_file(self, id: int, content: bytes):
        self.save(id, content, 'beatmaps')
        self.save_to_cache(
            name=f'osu:{id}',
            content=content,
            expiry=timedelta(days=1)
        )

    def upload_background(self, set_id: int, content: bytes):
        self.save(set_id, content, 'thumbnails')
        self.save_to_cache(
            name=f'mt:{set_id}l',
            content=content,
            expiry=timedelta(days=1)
        )

    def upload_mp3(self, set_id: int, content: bytes):
        self.save(set_id, content, 'audio')
        self.save_to_cache(
            name=f'mp3:{set_id}',
            content=content,
            expiry=timedelta(days=1)
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
        self.remove(id, 'replays')

    def remove_beatmap_file(self, beatmap_id: int):
        self.logger.debug(f'Removing beatmap file with id "{beatmap_id}"...')
        self.remove_from_cache(f'osu:{beatmap_id}')
        self.remove(beatmap_id, 'beatmaps')

    def remove_osz(self, set_id: int):
        self.logger.debug(f'Removing osz with id "{set_id}"...')
        self.remove(set_id, 'osz')

    def remove_osz2(self, set_id: int):
        self.logger.debug(f'Removing osz2 with id "{set_id}"...')
        self.remove(set_id, 'osz2')

    def remove_background(self, set_id: int):
        self.logger.debug(f'Removing background with id "{set_id}"...')
        self.remove_from_cache(f'mt:{set_id}l')
        self.remove(set_id, 'thumbnails')

    def remove_mp3(self, set_id: int):
        self.logger.debug(f'Removing mp3 with id "{set_id}"...')
        self.remove_from_cache(f'mp3:{set_id}')
        self.remove(set_id, 'audio')

    def remove_avatar(self, id: int):
        self.logger.debug(f'Removing avatar with id "{id}"...')
        self.remove_from_cache(f'avatar:{id}')
        self.remove(id, 'avatars')

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

    def remove(self, key: str, bucket: str) -> bool:
        """Remove a file from the specified bucket/directory."""
        if config.S3_ENABLED:
            return self.remove_from_s3(str(key), bucket)
        else:
            return self.remove_file(f'{bucket}/{key}')

    def save_to_cache(self, name: str, content: bytes, expiry=timedelta(days=1), override=True) -> bool:
        if len(content) > 40_000_000: return True
        return self.cache.set(str(name), content, expiry, nx=(not override))

    def get_from_cache(self, name: str) -> bytes | None:
        return self.cache.get(str(name))

    def remove_from_cache(self, name: str) -> bool:
        return self.cache.delete(str(name))

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
        except Exception as e:
            self.logger.error(f'Failed to read file "{filepath}": {e}')

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
            return
        except Exception as e:
            self.logger.error(f'Failed to download "{key}" from s3: "{e}"')
            return

        return buffer.getvalue()

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
            return []

        try:
            return {
                object['Key']: object['ETag'].replace('"', '')
                for object in self.s3.list_objects(Bucket=bucket)['Contents']
            }
        except Exception as e:
            self.logger.error(f'Failed to get etags: {e}')
            return []

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
            return

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
            return
