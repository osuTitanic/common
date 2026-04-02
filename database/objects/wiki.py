
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    ForeignKey,
    Computed,
    DateTime,
    Integer,
    Column,
    String
)

from datetime import datetime
from typing import List, Any
from .base import Base

class DBWikiPage(Base):
    __tablename__ = "wiki_pages"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String)
    path: Mapped[str] = mapped_column('path', String)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column('last_updated', DateTime, server_default=func.now())
    category_id: Mapped[int] = mapped_column('category_id', Integer, ForeignKey('wiki_categories.id'))

    category: Mapped['DBWikiCategory'] = relationship('DBWikiCategory', back_populates='pages')
    content: Mapped['DBWikiContent'] = relationship('DBWikiContent', back_populates='page')

class DBWikiCategory(Base):
    __tablename__ = "wiki_categories"

    id: Mapped[int] = mapped_column('id', Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String)
    translations: Mapped[Any] = mapped_column('translations', JSONB, default={})
    parent_id: Mapped[int] = mapped_column('parent_id', Integer, ForeignKey('wiki_categories.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    parent: Mapped['DBWikiCategory'] = relationship('DBWikiCategory', remote_side=[id])
    pages: Mapped[List['DBWikiPage']] = relationship('DBWikiPage', back_populates='category')

class DBWikiContent(Base):
    __tablename__ = "wiki_content"

    page_id: Mapped[int] = mapped_column('page_id', Integer, ForeignKey('wiki_pages.id'), primary_key=True)
    language: Mapped[str] = mapped_column('language', String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column('last_updated', DateTime, server_default=func.now())
    title: Mapped[str] = mapped_column('title', String)
    content: Mapped[str] = mapped_column('content', String)

    search: Mapped[Any] = mapped_column('search', TSVECTOR, Computed(
        "to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, ''))",
        persisted=True
    ))

    page: Mapped['DBWikiPage'] = relationship('DBWikiPage', back_populates='content')

class DBWikiOutlink(Base):
    __tablename__ = "wiki_outlinks"

    page_id: Mapped[int] = mapped_column('page_id', Integer, ForeignKey('wiki_pages.id'), primary_key=True)
    target_id: Mapped[int] = mapped_column('target_id', Integer, ForeignKey('wiki_pages.id'), primary_key=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, server_default=func.now())

    page: Mapped['DBWikiPage'] = relationship('DBWikiPage', foreign_keys=[page_id])
    target: Mapped['DBWikiPage'] = relationship('DBWikiPage', foreign_keys=[target_id])
