
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey,
    DateTime,
    Boolean,
    Integer,
    Column,
    String,
    ARRAY,
    Date,
    Text
)

from typing import Any
from datetime import datetime
from .forums import DBForumTopic
from .users import DBUser
from .base import Base

class DBRelease(Base):
    __tablename__ = "releases_titanic"

    name: Mapped[str] = mapped_column('name', String, primary_key=True)
    version: Mapped[int] = mapped_column('version', Integer)
    description: Mapped[str] = mapped_column('description', String, default='')
    category: Mapped[str] = mapped_column('category', String, default='Uncategorized')
    known_bugs: Mapped[str | None] = mapped_column('known_bugs', String, nullable=True)
    supported: Mapped[bool] = mapped_column('supported', Boolean, default=True)
    preview: Mapped[bool] = mapped_column('preview', Boolean, default=False)
    downloads: Mapped[str] = mapped_column('downloads', ARRAY(String), default=[])
    screenshots: Mapped[str] = mapped_column('screenshots', ARRAY(String), default=[])
    hashes: Mapped[Any] = mapped_column('hashes', JSONB, default=[])
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

class DBModdedRelease(Base):
    __tablename__ = "releases_modding"

    name: Mapped[str] = mapped_column('name', String, primary_key=True)
    description: Mapped[str] = mapped_column('description', String)
    creator_id: Mapped[int] = mapped_column('creator_id', Integer, ForeignKey('users.id'))
    topic_id: Mapped[int] = mapped_column('topic_id', Integer, ForeignKey('forum_topics.id'))
    client_version: Mapped[int] = mapped_column('client_version', Integer)
    client_extension: Mapped[str] = mapped_column('client_extension', String)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    creator: Mapped['DBUser'] = relationship('DBUser')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic')

class DBModdedReleaseEntries(Base):
    __tablename__ = "releases_modding_entries"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    mod_name: Mapped[str] = mapped_column('mod_name', String, ForeignKey('releases_modding.name'), nullable=False)
    version: Mapped[str] = mapped_column('version', String, nullable=False)
    stream: Mapped[str] = mapped_column('stream', String, nullable=False)
    checksum: Mapped[str] = mapped_column('checksum', String(32), nullable=False)
    download_url: Mapped[str | None] = mapped_column('download_url', String, nullable=True)
    update_url: Mapped[str | None] = mapped_column('update_url', String, nullable=True)
    post_id: Mapped[int] = mapped_column('post_id', Integer, ForeignKey('forum_posts.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

class DBModdedReleaseChangelog(Base):
    __tablename__ = "releases_modding_changelog"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column('entry_id', Integer, ForeignKey('releases_modding_entries.id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column('text', Text, nullable=False)
    type: Mapped[str] = mapped_column('type', Text, nullable=False)
    branch: Mapped[str] = mapped_column('branch', Text, nullable=False)
    author: Mapped[str] = mapped_column('author', Text, nullable=False)
    author_id: Mapped[int] = mapped_column('author_id', Integer, ForeignKey('users.id'), nullable=True)
    area: Mapped[str] = mapped_column('area', Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

class DBExtraRelease(Base):
    __tablename__ = "releases_extra"

    name: Mapped[str] = mapped_column('name', String, primary_key=True)
    description: Mapped[str] = mapped_column('description', String)
    download: Mapped[str] = mapped_column('download', String)
    filename: Mapped[str] = mapped_column('filename', String)
    md5: Mapped[str] = mapped_column('md5', String(32))

    @property
    def encoded_description(self) -> str:
        return self.description.replace(' ', '-')

class DBReleasesOfficial(Base):
    __tablename__ = "releases_official"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    version: Mapped[int] = mapped_column('version', Integer, nullable=False)
    stream: Mapped[str] = mapped_column('stream', Text, nullable=False)
    subversion: Mapped[int] = mapped_column('subversion', Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    files: Mapped[list['DBReleaseFiles']] = relationship(
        'DBReleaseFiles',
        secondary='releases_official_entries',
        back_populates='official_releases'
    )

class DBReleasesOfficialEntries(Base):
    __tablename__ = "releases_official_entries"

    release_id: Mapped[int] = mapped_column('release_id', Integer, ForeignKey('releases_official.id', ondelete='CASCADE'), primary_key=True)
    file_id: Mapped[int] = mapped_column('file_id', Integer, ForeignKey('releases_official_files.id', ondelete='CASCADE'), primary_key=True)

class DBReleaseFiles(Base):
    __tablename__ = "releases_official_files"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column('filename', Text, nullable=False)
    file_version: Mapped[int] = mapped_column('file_version', Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column('file_hash', String(32), nullable=False)
    filesize: Mapped[int] = mapped_column('filesize', Integer, nullable=False)
    patch_id: Mapped[str] = mapped_column('patch_id', Text, nullable=True)
    url_full: Mapped[str] = mapped_column('url_full', Text, nullable=False)
    url_patch: Mapped[str] = mapped_column('url_patch', Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column('timestamp', DateTime, server_default=func.now())

    official_releases: Mapped[list['DBReleasesOfficial']] = relationship(
        'DBReleasesOfficial',
        secondary='releases_official_entries',
        back_populates='files'
    )

class DBReleaseChangelog(Base):
    __tablename__ = "releases_official_changelog"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column('text', Text, nullable=False)
    type: Mapped[str] = mapped_column('type', Text, nullable=False)
    branch: Mapped[str] = mapped_column('branch', Text, nullable=False)
    author: Mapped[str] = mapped_column('author', Text, nullable=False)
    area: Mapped[str] = mapped_column('area', Text, nullable=True)
    created_at: Mapped[datetime.date] = mapped_column('created_at', Date, nullable=False, server_default=func.current_date())

    @property
    def prefixed_text(self) -> str:
        if not self.area:
            return self.text
        return f"{self.area.strip()}: {self.text}"

    @property
    def type_symbol(self) -> str:
        match self.type.lower():
            case 'add':
                return '+'
            case 'remove':
                return '-'
            case 'fix':
                return '*'
            case 'important':
                return '+'
            case _:
                return ''
