
from __future__ import annotations

import traceback
import requests
import config
import app

def call(content: str, exc_info: Exception | None = None) -> None:
    """Send logs to the officer webhook"""
    app.session.logger.warning(content)
    app.session.logger.debug('Calling officer...')

    if not config.MURDOCH_WEBHOOK_URL:
        app.session.logger.debug('Officer is not on board.')
        return

    if exc_info is not None:
        content += '```'
        content += '\n\n' + ''.join(
            traceback.format_exception(exc_info)
        )
        content += '```'

    payload = {'content': content}
    response = requests.post(config.MURDOCH_WEBHOOK_URL, json=payload)
    
    if not response.ok:
        app.session.logger.warning(
            f'Failed to call officer: {response.text}'
        )
        return

    app.session.logger.debug(
        f'Officer called successfully: {response.text}'
    )
