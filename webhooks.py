
# Modified webhook code from:
# https://github.com/osuAkatsuki/bancho.py/blob/master/app/discord.py

from __future__ import annotations

from dataclasses import dataclass, field
from requests import Response
from datetime import datetime, timezone
from typing import Any, List

import app

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
        file: Any | None = None,
        embeds: List[Embed] = []
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
            "Webhook must contain at least one " "of (content, file, embeds)."
        )

        if self.content and len(self.content) > 2000:
            # Truncate content if it's too long
            self.content = self.content[:1997] + "..."

        payload: dict[str, Any] = {"embeds": []}

        for key in ("content", "username", "avatar_url", "tts", "file"):
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

    def ensure_avatar_caching_disabled(self) -> None:
        if type(self.avatar_url) != str:
            return

        # Prevent Discord caching avatars indefinetly, only cache for 1 day
        now: datetime = datetime.now(timezone.utc)
        epoch: datetime = datetime(1970, 1, 1, tzinfo=timezone.utc)
        days_since_epoch = (now - epoch).days
        self.avatar_url = f"{self.avatar_url}?t={days_since_epoch}"

    def post(self) -> bool:
        """Post the webhook in json format"""
        try:
            app.session.requests.post(
                self.url,
                json=self.json,
                headers={
                    "Content-Type": (
                        "application/json"
                        if self.file is None
                        else "multipart/form-data"
                    )
                }
            ).raise_for_status()
            return True
        except Exception as e:
            app.session.logger.info(
                f"Failed to post webhook: {e}",
                exc_info=e
            )
            return False
