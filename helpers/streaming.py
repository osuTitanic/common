
from typing import IO, Generator
from zipstream import ZipStream
from pathlib import PurePath
from zipfile import ZipFile

video_file_extensions = frozenset((
    ".wmv", ".flv", ".mp4",
    ".avi", ".m4v", ".mpg",
    ".mov", ".webm", ".mkv",
    ".ogv", ".mpeg", ".3gp"
))

class NoVideoZipIterator:
    """An iterator that streams a zip file while excluding video files"""

    def __init__(self, source: IO[bytes]) -> None:
        self.closed: bool = False
        self.source: IO[bytes] | None = source
        self.source_zip = ZipFile(source, 'r')
        self.zip_stream = ZipStream(sized=True)
        self.iterator: Generator | None = None
        self.prepare_stream()

    def __len__(self) -> int:
        assert self.zip_stream is not None
        return len(self.zip_stream)

    def __iter__(self) -> Generator[bytes, None, None]:
        return self # type: ignore

    def __del__(self) -> None:
        self.close()

    def __next__(self) -> bytes:
        if self.closed:
            raise StopIteration

        if self.iterator is None:
            assert self.zip_stream is not None
            self.iterator = iter(self.zip_stream)

        try:
            return next(self.iterator)
        except StopIteration:
            self.close()
            raise

    def prepare_stream(self) -> None:
        assert self.zip_stream is not None
        assert self.source_zip is not None

        for item in self.source_zip.infolist():
            extension = PurePath(item.filename).suffix.lower()

            if extension in video_file_extensions:
                continue

            # Add each file as a chunked iterator instead
            # of reading its full contents into memory
            self.zip_stream.add(
                self.stream_file(item.filename),
                arcname=item.filename,
                size=item.file_size,
            )

    def stream_file(self, filename: str, chunk_size: int = 1024 * 64) -> Generator[bytes, None, None]:
        if not self.source_zip:
            return

        with self.source_zip.open(filename, 'r') as entry:
            while chunk := entry.read(chunk_size):
                yield chunk

    def close(self) -> None:
        if self.closed:
            return

        self.closed = True

        if self.source_zip is not None:
            self.source_zip.close()

        if self.source is not None:
            self.source.close()

        self.zip_stream = None
        self.source_zip = None
        self.source = None
        self.iterator = None
