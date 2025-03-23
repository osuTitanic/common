

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

    for file in release.hashes:
        if file.endswith('.exe') and hash in release.hashes[file]:
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
