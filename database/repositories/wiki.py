
from __future__ import annotations
from .wrapper import session_wrapper

from app.common.database.objects import DBWikiPage, DBWikiContent, DBWikiOutlink, DBWikiCategory
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from contextlib import suppress
from typing import List, Tuple
from datetime import datetime

import re

@session_wrapper
def create_page(
    name: str,
    path: str,
    content: str,
    language: str = 'en',
    session: Session = ...
) -> Tuple[DBWikiPage, DBWikiContent]:
    session.add(page := DBWikiPage(name=name, path=path))
    session.flush()
    session.refresh(page)
    content = create_content_entry(
        page_id=page.id,
        title=name,
        content=content,
        language=language,
        session=session
    )
    return page, content

@session_wrapper
def create_content_entry(
    page_id: int,
    title: str,
    content: str,
    language: str,
    session: Session = ...
) -> DBWikiContent:
    session.add(
        content := DBWikiContent(
            page_id=page_id,
            title=title,
            content=content,
            language=language
        )
    )
    session.flush()
    session.refresh(content)
    return content

@session_wrapper
def create_outlink(
    page_id: int,
    target_id: int,
    session: Session = ...
) -> DBWikiOutlink:
    session.add(
        outlink := DBWikiOutlink(
            page_id=page_id,
            target_id=target_id
        )
    )
    session.flush()
    session.refresh(outlink)
    return outlink

@session_wrapper
def fetch_page_by_id(
    page_id: int,
    session: Session = ...
) -> DBWikiPage:
    return session.query(DBWikiPage) \
        .filter(DBWikiPage.id == page_id) \
        .first()

@session_wrapper
def fetch_page_by_name(
    name: str,
    session: Session = ...
) -> DBWikiPage:
    return session.query(DBWikiPage) \
        .filter(DBWikiPage.name.ilike(name)) \
        .first()

@session_wrapper
def fetch_page_by_path(
    path: str,
    session: Session = ...
) -> DBWikiPage:
    return session.query(DBWikiPage) \
        .filter(DBWikiPage.path.ilike(path)) \
        .first()

@session_wrapper
def fetch_content(
    page_id: int,
    language: str,
    session: Session = ...
) -> DBWikiContent:
    return session.query(DBWikiContent) \
        .filter(DBWikiContent.page_id == page_id) \
        .filter(DBWikiContent.language == language) \
        .first()

@session_wrapper
def fetch_translated_page_title(
    page_id: int,
    language: str,
    session: Session = ...
) -> str | None:
    return session.query(DBWikiContent.title) \
        .filter(DBWikiContent.page_id == page_id) \
        .filter(DBWikiContent.language == language) \
        .scalar()

@session_wrapper
def fetch_languages(session: Session = ...) -> List[str]:
    return session.query(DBWikiContent.language) \
        .distinct() \
        .all()

@session_wrapper
def fetch_page_count(session: Session = ...) -> int:
    return session.query(DBWikiPage).count()

@session_wrapper
def search(
    query: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBWikiContent]:
    sanitized_query = re.sub(
        r'[^\w\s]', '',
        query
    )

    words = [
        word.strip()
        for word in sanitized_query.split()
    ]

    main_tsquery = func.plainto_tsquery(
        'simple',
        query
    )

    fuzzy_tsquery = func.to_tsquery(
        'simple',
        ' & '.join(f'{word}:*' for word in words)
    )

    return session.query(DBWikiContent) \
        .filter(or_(
            DBWikiContent.search.op('@@')(main_tsquery),
            DBWikiContent.search.op('@@')(fuzzy_tsquery)
        )) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def update_content(
    page_id: int,
    language: str,
    content: str,
    title: str | None = None,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiContent) \
        .filter(DBWikiContent.page_id == page_id) \
        .filter(DBWikiContent.language == language) \
        .update({
            'content': content,
            'last_updated': datetime.now(),
            'title': title or DBWikiContent.title
        })
    session.flush()
    return rows

@session_wrapper
def delete_page(
    page_id: int,
    session: Session = ...
) -> int:
    # Try to delete all related content and outlinks first
    with suppress(Exception):
        delete_content(page_id=page_id, session=session)
        delete_outlinks(page_id=page_id, session=session)

    rows = session.query(DBWikiPage) \
        .filter(DBWikiPage.id == page_id) \
        .delete()
    session.flush()
    return rows

@session_wrapper
def delete_content(
    page_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiContent) \
        .filter(DBWikiContent.page_id == page_id) \
        .delete()
    session.flush()
    return rows

@session_wrapper
def delete_outlinks(
    page_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiOutlink) \
        .filter(DBWikiOutlink.page_id == page_id) \
        .delete()
    session.flush()
    return rows

@session_wrapper
def fetch_main_categories(session: Session = ...) -> List[DBWikiCategory]:
    return session.query(DBWikiCategory) \
        .filter(DBWikiCategory.parent_id == None) \
        .order_by(DBWikiCategory.id.asc()) \
        .all()

@session_wrapper
def fetch_subcategories(
    parent_id: int,
    session: Session = ...
) -> List[DBWikiCategory]:
    return session.query(DBWikiCategory) \
        .filter(DBWikiCategory.parent_id == parent_id) \
        .order_by(DBWikiCategory.id.asc()) \
        .all()
