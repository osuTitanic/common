
# Modified webhook code from:
# https://github.com/osuAkatsuki/bancho.py/blob/master/app/discord.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Tuple

import requests
import json

@dataclass
class Footer:
    text: str
    icon_url: str | None = None
    proxy_icon_url: str | None = None

@dataclass
class Image:
    url: str
    proxy_url: str | None = None
    height: int | None = None
    width: int | None = None

@dataclass
class Thumbnail:
    url: str
    proxy_url: str | None = None
    height: int | None = None
    width: int | None = None

@dataclass
class Video:
    url: str
    height: int | None = None
    width: int | None = None

@dataclass
class Provider:
    url: str | None = None
    name: str | None = None

@dataclass
class Author:
    name: str | None = None
    url: str | None = None
    icon_url: str | None = None
    proxy_icon_url: str | None = None

@dataclass
class Field:
    name: str
    value: str
    inline: bool = False

@dataclass
class Embed:
    title: str | None = None
    type: str | None = None
    description: str | None = None
    url: str | None = None
    timestamp: datetime | None = None
    color: int | None = 0x000000
    footer: Footer | None = None
    image: Image | None = None
    thumbnail: Thumbnail | None = None
    video: Video | None = None
    provider: Provider | None = None
    author: Author | None = None
    fields: List[Field] = field(default_factory=list)

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        self.fields.append(Field(name, value, inline))

class Webhook:
    """A class to represent a single-use Discord webhook"""

    def __init__(
        self,
        url: str,
        content: str | None = None,
        username: str | None = None,
        avatar_url: str | None = None,
        is_tts: bool | None = None,
        file: Tuple[str, bytes] | None = None,
        embeds: List[Embed] = [],
    ) -> None:
        self.url = url
        self.content = content
        self.username = username
        self.avatar_url = avatar_url
        self.tts = is_tts
        self.file = file
        self.embeds = embeds
        self.ensure_avatar_caching_disabled()

    @property
    def json(self) -> Any:
        assert any([self.content, self.file, self.embeds]), (
            "Webhook must contain at least one of (content, file, embeds)."
        )

        if self.content and len(self.content) > 2000:
            # Truncate content if it's too long
            self.content = self.content[:1997] + "..."

        payload: dict[str, Any] = {"embeds": []}

        for key in ("content", "username", "avatar_url", "tts"):
            val = getattr(self, key)
            if val is not None:
                payload[key] = val

        for embed in self.embeds:
            embed_payload = {}

            # Simple params
            for key in ("title", "type", "description", "url", "timestamp", "color"):
                val = getattr(embed, key)
                if val is not None:
                    embed_payload[key] = val

            # Class params, must turn into dict
            for key in ("footer", "image", "thumbnail", "video", "provider", "author"):
                val = getattr(embed, key)
                if val is not None:
                    embed_payload[key] = val.__dict__

            if embed.fields:
                embed_payload["fields"] = [f.__dict__ for f in embed.fields]

            payload["embeds"].append(embed_payload)

        return payload

    def add_embed(self, embed: Embed) -> None:
        self.embeds.append(embed)

    def set_file(self, filename: str, data: bytes) -> None:
        self.file = (filename, data)

    def ensure_avatar_caching_disabled(self) -> None:
        """Prevent Discord from caching avatars indefinetly, only cache for 1 day"""
        if type(self.avatar_url) != str:
            return

        now: datetime = datetime.now(timezone.utc)
        epoch: datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
        days_since_epoch = (now - epoch).days
        self.avatar_url = f"{self.avatar_url}?t={days_since_epoch}"

    def post(self) -> bool:
        """Post the webhook"""
        if self.file is None:
            response = requests.post(
                self.url,
                json=self.json,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "osuTitanic/officer"
                }
            )
            return response.ok

        response = requests.post(
            self.url,
            headers={"User-Agent": "osuTitanic/officer"},
            data={"payload_json": json.dumps(self.json)},
            files={"file": self.file},
        )
        return response.ok
