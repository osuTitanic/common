

from ..database.repositories import releases
from sqlalchemy.orm import Session
from typing import List

@releases.session_wrapper
def is_valid_client_hash(version: int, hash: str, session: Session = ...) -> bool:
    if is_official_release(version, hash, session):
        return True

    if hash in fetch_hashes(version, session):
        return True
    
    return False

@releases.session_wrapper
def is_official_release(version: int, hash: str, session: Session = ...) -> bool:
    if not (file := releases.fetch_official_file_by_checksum(hash, session)):
        return False

    if file.filename != "osu!.exe":
        return False

    if not file.official_releases:
        return False

    for release in file.official_releases:
        if release.version == version:
            return True

    return False

@releases.session_wrapper
def is_valid_mod(identifier: str, hash: str, session: Session = ...) -> bool:
    if not (release := releases.fetch_modded(identifier, session)):
        return False

    if not releases.modded_entry_exists(release.name, hash, session):
        return False

    return True

@releases.session_wrapper
def fetch_hashes(version: int, session: Session = ...) -> List[str]:
    release_hashes = releases.fetch_hashes(version, session)

    if not release_hashes:
        return []

    return [
        hash
        for release in release_hashes
        for file in release[0]
        for hash in file['md5']
    ]
