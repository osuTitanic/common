

from ..database.repositories import releases
from sqlalchemy.orm import Session
from typing import List

@releases.session_wrapper
def is_valid_client_hash(version: int, hash: str, session: Session = ...) -> bool:
    hashes = fetch_hashes(version, session)
    return hash in hashes

@releases.session_wrapper
def is_valid_mod(identifier: str, hash: str, session: Session = ...) -> bool:
    if not (release := releases.fetch_modded(identifier)):
        return False

    for entry in release.hashes:
        if entry['file'].endswith('.exe') and hash in entry['md5']:
            return True

    return False

@releases.session_wrapper
def fetch_hashes(version: int, session: Session = ...) -> List[str]:
    return [
        hash
        for release in releases.fetch_hashes(version, session) or []
        for entry in release[0]
        for hash in entry['md5']
        if entry['file'].startswith('osu') and entry['file'].endswith('.exe')
    ]

@releases.session_wrapper
def fetch_hashes_by_filename(filename: str, session: Session = ...) -> List[str]:
    return [
        hash
        for release in releases.fetch_all(session)
        for file in release.hashes
        if file['file'] == filename
        for hash in file['md5']
    ]
