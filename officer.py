
from __future__ import annotations

from app.common import webhooks
from datetime import datetime
from typing import Any, List

import traceback
import config
import app

def call(content: str, exc_info: Exception | None = None) -> bool:
    """Send logs to the officer webhook"""
    app.session.logger.warning(content, exc_info=exc_info)
    app.session.logger.debug('Calling officer...')

    if not config.OFFICER_WEBHOOK_URL:
        app.session.logger.debug('Officer is not on board.')
        return

    if exc_info is not None:
        content += '```'
        content += '\n\n' + ''.join(
            traceback.format_exception(exc_info, limit=2)
        )[:1950]
        content += '```'

    return webhooks.Webhook(
        config.OFFICER_WEBHOOK_URL,
        content=content
    ).post()

def embed(
    title: str | None = None,
    type: str | None = None,
    description: str | None = None,
    url: str | None = None,
    timestamp: datetime | None = None,
    color: int | None = 0x000000,
    footer: webhooks.Footer | None = None,
    image: webhooks.Image | None = None,
    thumbnail: webhooks.Thumbnail | None = None,
    video: webhooks.Video | None = None,
    provider: webhooks.Provider | None = None,
    author: webhooks.Author | None = None,
    fields: List[webhooks.Field] = []
) -> bool:
    """Send an embed to the officer webhook"""
    app.session.logger.debug('Sending embed to officer...')

    if not config.OFFICER_WEBHOOK_URL:
        app.session.logger.debug('Officer is not on board.')
        return

    return webhooks.Webhook(
        config.OFFICER_WEBHOOK_URL,
        embeds=[webhooks.Embed(
            title, type, description,
            url, timestamp, color,
            footer, image, thumbnail,
            video, provider, author, fields
        )]
    ).post()

def event(
    content: str | None = None,
    username: str | None = None,
    avatar_url: str | None = None,
    is_tts: bool | None = None,
    file: Any | None = None,
    embeds: List[webhooks.Embed] = []
) -> bool:
    """Send an event to the event webhook"""
    app.session.logger.debug('Sending event to discord...')

    if not config.EVENT_WEBHOOK_URL:
        app.session.logger.debug('Event webhook was not configured.')
        return

    return webhooks.Webhook(
        config.EVENT_WEBHOOK_URL,
        content, username,
        avatar_url, is_tts,
        file, embeds
    ).post()
