
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship
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

from .forums import DBForumTopic
from .users import DBUser
from .base import Base

class DBRelease(Base):
    __tablename__ = "releases_titanic"

    name        = Column('name', String, primary_key=True)
    version     = Column('version', Integer)
    description = Column('description', String, default='')
    category    = Column('category', String, default='Uncategorized')
    known_bugs  = Column('known_bugs', String, nullable=True)
    supported   = Column('supported', Boolean, default=True)
    preview     = Column('preview', Boolean, default=False)
    downloads   = Column('downloads', ARRAY(String), default=[])
    screenshots = Column('screenshots', ARRAY(String), default=[])
    hashes      = Column('hashes', JSONB, default=[])
    created_at  = Column('created_at', DateTime, server_default=func.now())

class DBModdedRelease(Base):
    __tablename__ = "releases_modding"

    name             = Column('name', String, primary_key=True)
    description      = Column('description', String)
    creator_id       = Column('creator_id', Integer, ForeignKey('users.id'))
    topic_id         = Column('topic_id', Integer, ForeignKey('forum_topics.id'))
    client_version   = Column('client_version', Integer)
    client_extension = Column('client_extension', String)
    hashes           = Column('hashes', JSONB, default=[])
    created_at       = Column('created_at', DateTime, server_default=func.now())

    creator: Mapped['DBUser'] = relationship('DBUser')
    topic: Mapped['DBForumTopic'] = relationship('DBForumTopic')

class DBModdedReleaseEntries(Base):
    __tablename__ = "releases_modding_entries"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    mod_name   = Column('mod_name', String, ForeignKey('releases_modding.name'), nullable=False)
    version    = Column('version', String, nullable=False)
    stream     = Column('stream', String, nullable=False)
    checksum   = Column('checksum', String(32), nullable=False)
    download_url = Column('download_url', String, nullable=True)
    update_url   = Column('update_url', String, nullable=True)
    post_id      = Column('post_id', Integer, ForeignKey('forum_posts.id'), nullable=True)
    created_at   = Column('created_at', DateTime, server_default=func.now())

class DBModdedReleaseChangelog(Base):
    __tablename__ = "releases_modding_changelog"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    entry_id   = Column('entry_id', Integer, ForeignKey('releases_modding_entries.id', ondelete='CASCADE'))
    text       = Column('text', Text, nullable=False)
    type       = Column('type', Text, nullable=False)
    branch     = Column('branch', Text, nullable=False)
    author     = Column('author', Text, nullable=False)
    author_id  = Column('author_id', Integer, ForeignKey('users.id'), nullable=True)
    area       = Column('area', Text, nullable=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

class DBExtraRelease(Base):
    __tablename__ = "releases_extra"

    name        = Column('name', String, primary_key=True)
    description = Column('description', String)
    download    = Column('download', String)
    filename    = Column('filename', String)
    md5         = Column('md5', String(32))
    
    @property
    def encoded_description(self) -> str:
        return self.description.replace(' ', '-')

class DBReleasesOfficial(Base):
    __tablename__ = "releases_official"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    version    = Column('version', Integer, nullable=False)
    stream     = Column('stream', Text, nullable=False)
    subversion = Column('subversion', Integer, nullable=False)
    created_at = Column('created_at', DateTime, server_default=func.now())

    files: Mapped[list['DBReleaseFiles']] = relationship(
        'DBReleaseFiles',
        secondary='releases_official_entries',
        backref='official_releases'
    )

class DBReleasesOfficialEntries(Base):
    __tablename__ = "releases_official_entries"

    release_id = Column('release_id', Integer, ForeignKey('releases_official.id', ondelete='CASCADE'), primary_key=True)
    file_id    = Column('file_id', Integer, ForeignKey('releases_official_files.id', ondelete='CASCADE'), primary_key=True)

class DBReleaseFiles(Base):
    __tablename__ = "releases_official_files"

    id           = Column('id', Integer, primary_key=True, autoincrement=True)
    filename     = Column('filename', Text, nullable=False)
    file_version = Column('file_version', Integer, nullable=False)
    file_hash    = Column('file_hash', String(32), nullable=False)
    filesize     = Column('filesize', Integer, nullable=False)
    patch_id     = Column('patch_id', Text, nullable=True)
    url_full     = Column('url_full', Text, nullable=False)
    url_patch    = Column('url_patch', Text, nullable=True)
    timestamp    = Column('timestamp', DateTime, server_default=func.now())

class DBReleaseChangelog(Base):
    __tablename__ = "releases_official_changelog"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    text       = Column('text', Text, nullable=False)
    type       = Column('type', Text, nullable=False)
    branch     = Column('branch', Text, nullable=False)
    author     = Column('author', Text, nullable=False)
    area       = Column('area', Text, nullable=True)
    created_at = Column('created_at', Date, nullable=False, server_default=func.current_date())

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
