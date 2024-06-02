
from __future__ import annotations
from .webhooks import Webhook

import traceback
import config
import app

def call(content: str, exc_info: Exception | None = None) -> None:
    """Send logs to the officer webhook"""
    app.session.logger.warning(content, exc_info=exc_info)
    app.session.logger.debug('Calling officer...')

    if not config.OFFICER_WEBHOOK_URL:
        app.session.logger.debug('Officer is not on board.')
        return

    if exc_info is not None:
        content += '```'
        content += '\n\n' + ''.join(
            traceback.format_exception(exc_info)
        )
        content += '```'

    Webhook(config.OFFICER_WEBHOOK_URL, content=content).post()
