
from __future__ import annotations
from typing import List

from app.common.database import DBBeatmapset, DBBeatmap
from app.common.database.repositories import wrapper
from app.common import officer

from dataclasses import dataclass, asdict, field
from sqlalchemy.orm import Session
from sqlalchemy import func

import base64
import config
import json
import app

@dataclass
class UploadRequest:
    set_id: int
    osz_ticket: str
    has_video: bool
    has_storyboard: bool
    metadata: dict
    is_update: bool = False
    tickets: List[UploadTicket] = field(default_factory=list)

    @property
    def files(self) -> dict:
        return {ticket.filename: ticket.file for ticket in self.tickets}

    @property
    def beatmaps(self) -> dict:
        return {ticket.filename: ticket.data for ticket in self.tickets}

    @property
    def osz_filename(self) -> str:
        return (
            f'{self.set_id} '
            f'{self.metadata["artist"]} - {self.metadata["title"]} '
            f'({self.metadata["author"]["username"]})'
            '.osz'
        )

@dataclass
class UploadTicket:
    filename: str
    ticket: str
    file: bytes
    data: dict

def register_upload_request(user_id: int, request: UploadRequest) -> None:
    request_dict = asdict(request)

    for ticket in request_dict['tickets']:
        # Serialize the binary file data to base64
        ticket['file'] = base64.b64encode(ticket['file']).decode()

    serialized_request = json.dumps(request_dict)
    app.session.redis.set(f'beatmap_upload:{user_id}', serialized_request, ex=3600)

def get_upload_request(user_id: int) -> UploadRequest | None:
    if not (serialized_request := app.session.redis.get(f'beatmap_upload:{user_id}')):
        return

    request_dict = json.loads(serialized_request)

    for ticket in request_dict['tickets']:
        # Deserialize the base64 file data to binary
        ticket['file'] = base64.b64decode(ticket['file'])

    tickets = [
        UploadTicket(**ticket)
        for ticket in request_dict['tickets']
    ]

    request = UploadRequest(**request_dict)
    request.tickets = tickets
    return request

def upload_request_exists(user_id: int) -> bool:
    return app.session.redis.exists(f'beatmap_upload:{user_id}')

def remove_upload_request(user_id: int) -> None:
    app.session.redis.delete(f'beatmap_upload:{user_id}')

@wrapper.session_wrapper
def next_beatmapset_id(session: Session = ...) -> int:
    """Get the next availabe beatmapset id"""
    while True:
        database_id = session.query(
            func.nextval('beatmapsets_id_seq')
        ).scalar()

        exists = session.query(DBBeatmapset.id) \
            .filter(DBBeatmapset.id == database_id) \
            .count() > 0

        if exists:
            continue

        return database_id

@wrapper.session_wrapper
def next_beatmap_id(session: Session = ...) -> int:
    """Get the next availabe beatmap id"""
    while True:
        database_id = session.query(
            func.nextval('beatmaps_id_seq')
        ).scalar()

        exists = session.query(DBBeatmap.id) \
            .filter(DBBeatmap.id == database_id) \
            .count() > 0

        if exists:
            continue

        return database_id

def process_on_fail(e: Exception) -> None:
    officer.call(f'Failed to process osz/osu file: "{e}"')

@wrapper.exception_wrapper(process_on_fail)
def decrypt_osz2(osz2_file: bytes) -> dict | None:
    if not config.OSZ2_SERVICE_URL:
        return

    response = app.session.requests.post(
        f'{config.OSZ2_SERVICE_URL}/osz2/decrypt',
        files={'osz2': osz2_file}
    )

    if not response.ok:
        officer.call(f'Failed to decrypt osz2 file: "{response.text}"')
        return

    return response.json()

@wrapper.exception_wrapper(process_on_fail)
def patch_osz2(patch_file: bytes, osz2: bytes) -> bytes | None:
    if not config.OSZ2_SERVICE_URL:
        return

    response = app.session.requests.post(
        f'{config.OSZ2_SERVICE_URL}/osz2/patch',
        files={
            'patch': patch_file,
            'osz2': osz2
        }
    )

    if not response.ok:
        officer.call(f'Failed to patch osz2 file: "{response.text}"')
        return

    return response.content

@wrapper.exception_wrapper(process_on_fail)
def parse_beatmap(osu_file: bytes) -> dict | None:
    if not config.OSZ2_SERVICE_URL:
        return

    response = app.session.requests.post(
        f'{config.OSZ2_SERVICE_URL}/osu/parse',
        files={'osu': osu_file}
    )

    if not response.ok:
        officer.call(f'Failed to parse osu file: "{response.text}"')
        return

    return response.json()
