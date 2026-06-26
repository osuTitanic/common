
from io import RawIOBase, SEEK_SET, SEEK_CUR, SEEK_END
from botocore.client import BaseClient
from typing import BinaryIO


class S3FileReader(RawIOBase, BinaryIO):
    """A read-only, file-like object that actually reads S3 files"""

    def __init__(
        self,
        s3: BaseClient,
        bucket: str,
        key: str,
        size: int
    ) -> None:
        self.s3 = s3
        self.bucket = bucket
        self.key = key
        self.size = size
        self.position = 0

    def __repr__(self) -> str:
        return f'<S3FileReader "{self.bucket}/{self.key}" ({self.size} bytes)>'

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def readall(self) -> bytes:
        return self.read(-1)

    def readinto(self, buffer) -> int:
        data = self.read(len(buffer))
        buffer[:len(data)] = data
        return len(data)

    def read(self, size: int = -1) -> bytes:
        if self.closed:
            raise ValueError('I/O operation on closed file')

        if self.position >= self.size:
            return b''

        if size is None or size < 0:
            # Read until the end of the object
            end = self.size - 1
        else:
            end = min(self.position + size, self.size) - 1

        if end < self.position:
            return b''

        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=self.key,
            Range=f'bytes={self.position}-{end}'
        )

        data = response['Body'].read()
        self.position += len(data)
        return data

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        if whence == SEEK_SET:
            # Set the position to offset
            position = offset
        elif whence == SEEK_CUR:
            # Move the position by offset
            position = self.position + offset
        elif whence == SEEK_END:
            # Move the position to the end of the file plus offset
            position = self.size + offset
        else:
            # grrr
            raise ValueError(f'Invalid whence value: {whence}')

        if position < 0:
            # grrr2
            raise ValueError('Negative seek position')

        self.position = position
        return self.position
