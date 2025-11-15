
from typing import List
from .base import Base

from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey,
    Computed,
    DateTime,
    Integer,
    Column,
    String
)

class DBWikiPage(Base):
    __tablename__ = "wiki_pages"

    id         = Column('id', Integer, primary_key=True, autoincrement=True)
    name       = Column('name', String)
    path       = Column('path', String)
    created_at = Column('created_at', DateTime, server_default=func.now())
    last_updated = Column('last_updated', DateTime, server_default=func.now())
    category_id = Column('category_id', Integer, ForeignKey('wiki_categories.id'))

    category: Mapped['DBWikiCategory'] = relationship('DBWikiCategory', back_populates='pages')
    content: Mapped['DBWikiContent'] = relationship('DBWikiContent', back_populates='page')

class DBWikiCategory(Base):
    __tablename__ = "wiki_categories"

    id           = Column('id', Integer, primary_key=True, autoincrement=True)
    name         = Column('name', String)
    translations = Column('translations', JSONB, default={})
    parent_id    = Column('parent_id', Integer, ForeignKey('wiki_categories.id'), nullable=True)
    created_at   = Column('created_at', DateTime, server_default=func.now())

    parent: Mapped['DBWikiCategory'] = relationship('DBWikiCategory', remote_side=[id])
    pages: Mapped[List['DBWikiPage']] = relationship('DBWikiPage', back_populates='category')

class DBWikiContent(Base):
    __tablename__ = "wiki_content"

    page_id      = Column('page_id', Integer, ForeignKey('wiki_pages.id'), primary_key=True)
    language     = Column('language', String, primary_key=True)
    created_at   = Column('created_at', DateTime, server_default=func.now())
    last_updated = Column('last_updated', DateTime, server_default=func.now())
    title        = Column('title', String)
    content      = Column('content', String)

    search = Column('search', TSVECTOR, Computed(
        "to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, ''))",
        persisted=True
    ))

    page: Mapped['DBWikiPage'] = relationship('DBWikiPage', back_populates='content')

class DBWikiOutlink(Base):
    __tablename__ = "wiki_outlinks"

    page_id    = Column('page_id', Integer, ForeignKey('wiki_pages.id'), primary_key=True)
    target_id  = Column('target_id', Integer, ForeignKey('wiki_pages.id'), primary_key=True)
    created_at = Column('created_at', DateTime, server_default=func.now())

    page: Mapped['DBWikiPage'] = relationship('DBWikiPage', foreign_keys=[page_id])
    target: Mapped['DBWikiPage'] = relationship('DBWikiPage', foreign_keys=[target_id])
