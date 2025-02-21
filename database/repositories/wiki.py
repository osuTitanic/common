
from __future__ import annotations

from app.common.database.objects import DBWikiPage, DBWikiContent, DBWikiOutlink
from sqlalchemy.orm import Session
from typing import List, Tuple
from datetime import datetime

from .wrapper import session_wrapper

@session_wrapper
def create_page(
    name: str,
    content: str,
    language: str = 'en',
    session: Session = ...
) -> Tuple[DBWikiPage, DBWikiContent]:
    session.add(page := DBWikiPage(name=name))
    session.commit()
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
    session.commit()
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
    session.commit()
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
def fetch_languages(session: Session = ...) -> List[str]:
    return session.query(DBWikiContent.language) \
        .distinct() \
        .all()

@session_wrapper
def update_content(
    page_id: int,
    language: str,
    content: str,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiContent) \
        .filter(DBWikiContent.page_id == page_id) \
        .filter(DBWikiContent.language == language) \
        .update({
            'content': content,
            'last_updated': datetime.now()
        })
    session.commit()
    return rows

@session_wrapper
def delete_page(
    page_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiPage) \
        .filter(DBWikiPage.id == page_id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def delete_content(
    page_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiContent) \
        .filter(DBWikiContent.page_id == page_id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def delete_outlinks(
    page_id: int,
    session: Session = ...
) -> int:
    rows = session.query(DBWikiOutlink) \
        .filter(DBWikiOutlink.page_id == page_id) \
        .delete()
    session.commit()
    return rows
