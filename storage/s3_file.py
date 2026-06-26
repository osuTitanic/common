
from io import RawIOBase, SEEK_SET, SEEK_CUR, SEEK_END
from botocore.client import BaseClient
from typing import BinaryIO


class S3FileReader(RawIOBase, BinaryIO):
    """A read-only, file-like object that actually reads S3 files"""

    # Amount of data to fetch per range request.
    # Consumers like zipfile read in tiny chunks, so without buffering,
    # every chunk would result in a ton of unnecessary requests.
    block_size = 6 * 1024 * 1024

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
        self.buffer = b''
        self.buffer_start = 0

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
            # Size specified to read everything
            data = self.fetch(self.position, self.size - 1)
            self.position += len(data)
            return data

        # Read a specific number of bytes, buffering as necessary
        result = bytearray()
        remaining = size

        while remaining > 0 and self.position < self.size:
            is_buffered = (
                self.buffer_start <= self.position < self.buffer_start + len(self.buffer)
            )

            if not is_buffered:
                # Requested position isn't buffered -> prefetch a new block
                end = min(self.position + self.block_size, self.size) - 1
                self.buffer = self.fetch(self.position, end)
                self.buffer_start = self.position

                if not self.buffer:
                    break

            # Use the buffered data to complete the read request
            offset = self.position - self.buffer_start
            chunk = self.buffer[offset:offset + remaining]
            result += chunk

            self.position += len(chunk)
            remaining -= len(chunk)

        return bytes(result)

    def fetch(self, start: int, end: int) -> bytes:
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=self.key,
            Range=f'bytes={start}-{end}'
        )
        return response['Body'].read()

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
