


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
    session.flush()
    return release

@session_wrapper
def create_official(
    version: int,
    subversion: int,
    created_at: datetime,
    stream: str = "stable",
    session: Session = ...
) -> DBReleasesOfficial:
    session.add(
        release := DBReleasesOfficial(
            version=version,
            subversion=subversion,
            stream=stream,
            created_at=created_at
        )
    )
    session.flush()
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
    session.flush()
    return entry

@session_wrapper
def create_modded_entry(
    mod_name: str,
    version: str,
    stream: str,
    checksum: str,
    download_url: str | None = None,
    update_url: str | None = None,
    post_id: int | None = None,
    session: Session = ...
) -> DBModdedRelease:
    session.add(
        entry := DBModdedReleaseEntries(
            mod_name=mod_name,
            version=version,
            stream=stream,
            checksum=checksum,
            download_url=download_url,
            update_url=update_url,
            post_id=post_id
        )
    )
    session.flush()
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
def fetch_modded_entry_by_id(mod_name: str, entry_id: int, session: Session = ...) -> DBModdedReleaseEntries | None:
    return session.query(DBModdedReleaseEntries) \
        .filter(DBModdedReleaseEntries.mod_name == mod_name) \
        .filter(DBModdedReleaseEntries.id == entry_id) \
        .first()

@session_wrapper
def fetch_modded_entry_by_checksum(mod_name: str, checksum: str, session: Session = ...) -> DBModdedReleaseEntries | None:
    return session.query(DBModdedReleaseEntries) \
        .filter(DBModdedReleaseEntries.mod_name == mod_name) \
        .filter(DBModdedReleaseEntries.checksum == checksum) \
        .first()

@session_wrapper
def fetch_modded_entries(
    mod_name: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = ...
) -> List[DBModdedReleaseEntries]:
    return session.query(DBModdedReleaseEntries) \
        .filter(DBModdedReleaseEntries.mod_name == mod_name) \
        .order_by(DBModdedReleaseEntries.created_at.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()

@session_wrapper
def modded_entry_exists(mod_name: str, checksum: str, session: Session = ...) -> bool:
    return session.query(DBModdedReleaseEntries.id) \
        .filter(DBModdedReleaseEntries.mod_name == mod_name) \
        .filter(DBModdedReleaseEntries.checksum == checksum) \
        .count() > 0

@session_wrapper
def update_modded_entry(
    entry_id: int,
    updates: dict,
    session: Session = ...
) -> int:
    rows = session.query(DBModdedReleaseEntries) \
        .filter(DBModdedReleaseEntries.id == entry_id) \
        .update(updates)
    session.flush()
    return rows

@session_wrapper
def delete_modded_entry(entry_id: int, session: Session = ...) -> int:
    rows = session.query(DBModdedReleaseEntries) \
        .filter(DBModdedReleaseEntries.id == entry_id) \
        .delete(synchronize_session=False)
    session.flush()
    return rows

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

@session_wrapper
def delete_official(release_id: int, session: Session = ...) -> int:
    rows = session.query(DBReleasesOfficial) \
        .filter(DBReleasesOfficial.id == release_id) \
        .delete(synchronize_session=False)
    session.flush()
    return rows
