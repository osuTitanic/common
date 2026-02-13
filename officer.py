
from app.common.config import config_instance as config
from typing import Any, List, Tuple
from app.common import webhooks
from datetime import datetime

import traceback
import app

def call(
    content: str | None = None,
    exc_info: Exception | None = None,
    exc_limit: int = 2,
    exc_offset: int = 0,
    file: Tuple[str, bytes] | None = None
) -> bool:
    """Send logs to the officer webhook"""
    app.session.logger.warning(content, exc_info=exc_info)
    app.session.logger.debug('Calling officer...')
    embeds: List[webhooks.Embed] = []

    if not config.OFFICER_WEBHOOK_URL:
        app.session.logger.debug('Officer is not on board.')
        return False

    if exc_info is not None:
        formatted_traceback = traceback.format_exception(exc_info, limit=exc_limit)
        formatted_traceback = formatted_traceback[exc_offset:]
        traceback_text = '```python\n' + ''.join(formatted_traceback)[:3512] + '```'

        exception_embed = webhooks.Embed(
            title="Exception Occurred",
            description=(
                f"**Component**\n{app.session.logger.name}\n\n"
                f"**Time**\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"**Exception Type**\n`{exc_info.__class__.__name__}`\n\n"
                f"**Exception Message**\n`{str(exc_info)}`\n\n"
                f"**Traceback**\n{traceback_text}"
            ),
            color=0xFF0000
        )
        embeds.append(exception_embed)

    return webhooks.Webhook(
        config.OFFICER_WEBHOOK_URL,
        content=content,
        embeds=embeds,
        file=file
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
        return False

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
    embeds: List[webhooks.Embed] = [],
    url: str = config.ANNOUNCE_EVENTS_WEBHOOK_URL
) -> bool:
    """Send an event to the event webhook"""
    app.session.logger.debug('Sending event to discord...')

    if not url:
        app.session.logger.debug('Event webhook was not configured.')
        return False

    return webhooks.Webhook(
        url,
        content, username,
        avatar_url, is_tts,
        file, embeds
    ).post()
