

from ..database import releases
from typing import List

def fetch_hashes(version: int) -> List[str]:
    return [
        hash
        for file in releases.fetch_hashes(version) or []
        for hash in file['md5']
    ]

def is_valid_client_hash(hash: str) -> bool:
    hashes = fetch_hashes()
    return hash in hashes
