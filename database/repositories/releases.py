


from __future__ import annotations

from app.common.database.objects.releases import *
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .wrapper import session_wrapper

@session_wrapper
def create(
    name: str,
    version: int,
    downloads: list,
    hashes: dict,
    screenshots: dict,
    session: Session = ...
) -> DBRelease:
    session.add(
        release := DBRelease(
            name=name,
            version=version,
            hashes=hashes
        )
    )
    session.refresh(release)
    session.commit()
    return release

@session_wrapper
def create_official(
    version: int,
    subversion: int,
    changelog: str,
    created_at: datetime,
    stream: str = "stable",
    session: Session = ...
) -> DBReleasesOfficial:
    session.add(
        release := DBReleasesOfficial(
            version=version,
            subversion=subversion,
            changelog=changelog,
            stream=stream,
            created_at=created_at
        )
    )
    session.refresh(release)
    session.commit()
    return release

@session_wrapper
def create_official_file_entry(
    release_id: int,
    file_id: int,
    session: Session = ...
) -> DBReleaseFiles:
    session.add(
        entry := DBReleasesOfficialEntries(
            release_id=release_id,
            file_id=file_id
        )
    )
    session.refresh(entry)
    session.commit()
    return entry

@session_wrapper
def fetch_by_version(version: int, session: Session = ...) -> DBRelease | None:
    return session.query(DBRelease) \
        .filter(DBRelease.version == version) \
        .first()

@session_wrapper
def fetch_all(session: Session = ...) -> List[DBRelease]:
    return session.query(DBRelease) \
        .order_by(DBRelease.version.desc()) \
        .all()

@session_wrapper
def fetch_hashes(version: int, session: Session = ...) -> List[dict]:
    return session.query(DBRelease.hashes) \
        .filter(DBRelease.version == version) \
        .all()

@session_wrapper
def fetch_modded(identifier: str, session: Session = ...) -> DBModdedRelease | None:
    return session.query(DBModdedRelease) \
        .filter(DBModdedRelease.client_extension == identifier) \
        .first()

@session_wrapper
def fetch_modded_all(session: Session = ...) -> List[DBModdedRelease]:
    return session.query(DBModdedRelease) \
        .order_by(DBModdedRelease.created_at.desc()) \
        .all()

@session_wrapper
def fetch_extras(session: Session = ...) -> List[DBExtraRelease]:
    return session.query(DBExtraRelease) \
        .order_by(DBExtraRelease.name.asc()) \
        .all()

@session_wrapper
def fetch_official_by_id(release_id: int, session: Session = ...) -> DBReleasesOfficial | None:
    return session.query(DBReleasesOfficial) \
        .filter(DBReleasesOfficial.id == release_id) \
        .first()

@session_wrapper
def fetch_official_by_version(version: int, session: Session = ...) -> DBReleasesOfficial | None:
    return session.query(DBReleasesOfficial) \
        .filter(DBReleasesOfficial.version == version) \
        .order_by(DBReleasesOfficial.subversion.desc()) \
        .first()

@session_wrapper
def fetch_official_range(
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBReleasesOfficial]:
    return session.query(DBReleasesOfficial) \
        .order_by(DBReleasesOfficial.version.desc(), DBReleasesOfficial.subversion.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def fetch_official_file_by_name(filename: str, session: Session = ...) -> DBReleaseFiles | None:
    return session.query(DBReleaseFiles) \
        .filter(DBReleaseFiles.filename == filename.strip()) \
        .order_by(DBReleaseFiles.id.desc()) \
        .first()

@session_wrapper
def fetch_official_file_by_checksum(checksum: str, session: Session = ...) -> DBReleaseFiles | None:
    return session.query(DBReleaseFiles) \
        .filter(DBReleaseFiles.file_hash == checksum) \
        .first()

@session_wrapper
def fetch_official_file_by_patch(patch_filename: str, session: Session = ...) -> DBReleaseFiles | None:
    return session.query(DBReleaseFiles) \
        .filter(DBReleaseFiles.url_patch.like(f'%{patch_filename}')) \
        .first()

@session_wrapper
def fetch_file_entries(release_id: int, session: Session = ...) -> List[DBReleaseFiles]:
    return session.query(DBReleaseFiles) \
        .join(DBReleasesOfficialEntries, DBReleasesOfficialEntries.file_id == DBReleaseFiles.id) \
        .filter(DBReleasesOfficialEntries.release_id == release_id) \
        .all()

@session_wrapper
def fetch_file_id_from_version(version: int, session: Session = ...) -> int | None:
    return session.query(DBReleaseFiles.id) \
        .filter(DBReleaseFiles.file_version == version) \
        .scalar() or None

@session_wrapper
def official_file_exists(checksum: str, session: Session = ...) -> bool:
    return session.query(DBReleaseFiles.id) \
        .filter(DBReleaseFiles.file_hash == checksum) \
        .count() > 0
