
from typing import BinaryIO, Generator, List, IO
from botocore.exceptions import ClientError
from botocore.config import Config as BotoConfig
from botocore.client import BaseClient
from boto3.s3.transfer import TransferConfig
from functools import cached_property

from .s3_file import S3FileReader
from .base import BaseStorage
from ..config import Config

import boto3
import io

class S3Storage(BaseStorage):
    """Storage backend that stores files in an S3-compatible service"""

    def __init__(self, config: Config) -> None:
        super().__init__(config)

        self.s3: BaseClient = boto3.client(
            's3',
            endpoint_url=self.config.S3_BASEURL,
            region_name=self.config.S3_REGION,
            aws_access_key_id=self.config.S3_ACCESS_KEY,
            aws_secret_access_key=self.config.S3_SECRET_KEY,
            config=BotoConfig(
                max_pool_connections=self.config.S3_MAX_POOL_CONNECTIONS,
                connect_timeout=self.config.S3_CONNECT_TIMEOUT,
                read_timeout=self.config.S3_READ_TIMEOUT,
                retries={
                    'max_attempts': self.config.S3_MAX_ATTEMPTS,
                    'mode': self.config.S3_RETRY_MODE
                }
            )
        )
        self.transfer_config = TransferConfig(
            multipart_threshold=self.config.S3_MULTIPART_THRESHOLD,
            multipart_chunksize=self.config.S3_MULTIPART_CHUNKSIZE,
            max_concurrency=self.config.S3_MAX_CONCURRENCY,
            max_io_queue=self.config.S3_MAX_IO_QUEUE,
            use_threads=self.config.S3_USE_THREADS
        )

    @cached_property
    def valid_s3_configuration(self) -> bool:
        try:
            self.s3.head_bucket(Bucket=self.config.S3_BUCKET)
            return True
        except Exception:
            return False

    def save(self, key: str, content: bytes | BinaryIO, bucket: str) -> bool:
        if bucket.endswith('/'):
            bucket = bucket[:-1]

        try:
            if isinstance(content, bytes):
                content = io.BytesIO(content)

            self.s3.upload_fileobj(
                content,
                self.config.S3_BUCKET,
                f"{bucket}/{key}",
                Config=self.transfer_config
            )
        except Exception as e:
            self.logger.error(f'Failed to upload "{key}" to s3: "{e}"')
            return False

        return True

    def get(self, key: str, bucket: str) -> bytes | None:
        buffer = io.BytesIO()

        try:
            self.s3.download_fileobj(
                self.config.S3_BUCKET,
                f"{bucket}/{key}",
                buffer,
                Config=self.transfer_config
            )
        except ClientError:
            # Most likely not found
            return None
        except Exception as e:
            self.logger.error(f'Failed to download "{key}" from s3: "{e}"')
            return None

        return buffer.getvalue()

    def get_iterator(self, key: str, bucket: str, chunk_size: int = 1024 * 64) -> Generator:
        try:
            response = self.s3.get_object(
                Bucket=self.config.S3_BUCKET,
                Key=f"{bucket}/{key}"
            )
            body = response['Body']

            while chunk := body.read(chunk_size):
                yield chunk
        except ClientError:
            # Most likely not found
            return
        except Exception as e:
            self.logger.error(f'Failed to download "{key}" from s3: "{e}"')
            return

    def get_io(self, key: str, bucket: str) -> IO[bytes] | None:
        size = self.get_size(key, bucket)

        if size is None:
            # Object most likely doesn't exist
            return None

        return S3FileReader(
            self.s3,
            self.config.S3_BUCKET,
            f"{bucket}/{key}",
            size
        )

    def get_size(self, key: str, bucket: str) -> int | None:
        try:
            response = self.s3.head_object(
                Bucket=self.config.S3_BUCKET,
                Key=f"{bucket}/{key}"
            )
            return response['ContentLength']
        except ClientError:
            return None
        except Exception as e:
            self.logger.error(f'Failed to get size of "{key}" from s3: "{e}"')
            return None

    def remove(self, key: str, bucket: str) -> bool:
        try:
            self.s3.delete_object(
                Bucket=self.config.S3_BUCKET,
                Key=f"{bucket}/{key}"
            )
        except Exception as e:
            self.logger.error(f'Failed to remove "{key}" from {bucket}: "{e}"')
            return False

        return True

    def file_exists(self, key: str, folder: str) -> bool:
        try:
            self.s3.head_object(
                Bucket=self.config.S3_BUCKET,
                Key=f"{folder}/{key}"
            )
            return True
        except ClientError:
            return False

    def list(self, key: str) -> List[str]:
        keys = []
        continuation_token = None

        while True:
            kwargs = {
                'Bucket': self.config.S3_BUCKET,
                'Prefix': key
            }
            if continuation_token:
                kwargs['ContinuationToken'] = continuation_token

            response = self.s3.list_objects_v2(**kwargs)

            if 'Contents' not in response:
                break

            keys.extend(obj['Key'] for obj in response['Contents'])

            if not response.get('IsTruncated'):
                break

            continuation_token = response['NextContinuationToken']

        return keys

    def get_presigned_url(self, folder: str, key: str, expiration: int = 900) -> str | None:
        try:
            return self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.config.S3_BUCKET,
                    'Key': f"{folder}/{key}"
                },
                ExpiresIn=expiration
            )
        except ClientError as e:
            self.logger.error(f'Failed to generate presigned url: {e}')
            return None

    def get_osz_internal_path(self, set_id) -> str | None:
        # No on-disk path for S3-backed osz files
        return None
