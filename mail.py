
from __future__ import annotations

from .database.objects import DBVerification, DBUser
from .constants import email

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import config
import app

client = SendGridAPIClient(config.SENDGRID_API_KEY)

def sendgrid(subject: str, message: str, email: str):
    message = Mail(
        from_email=config.SENDGRID_EMAIL,
        to_emails=email,
        subject=subject,
        html_content=message.replace('\n', '<br>')
    )

    response = client.send(message)

    if response.status_code != 200:
        app.session.logger.warning(
            f'Failed to send email: {response.body}'
        )

    return response

def mailgun(subject: str, message: str, email: str):
    response = app.session.requests.post(
        f'https://{config.MAILGUN_URL}/v3/{config.MAILGUN_DOMAIN}/messages',
        auth=('api', config.MAILGUN_API_KEY),
        data={
            'from': f'Titanic <{config.MAILGUN_EMAIL}>',
            'to': [email],
            'subject': subject,
            'html': message.replace('\n', '<br>')
        }
    )

    if not response.ok:
        app.session.logger.warning(
            f'Failed to send email: {response.text}'
        )

    return response

def send(subject: str, message: str, email: str):
    app.session.logger.info(f'Sending email to {email} with subject "{subject}"...')

    if not config.EMAILS_ENABLED:
        app.session.logger.warning(f'Failed to send email: Emails are disabled.')
        return

    if config.SENDGRID_API_KEY:
        return sendgrid(subject, message, email)

    if config.MAILGUN_API_KEY:
        return mailgun(subject, message, email)

def send_welcome_email(verification: DBVerification, user: DBUser):
    message = email.WELCOME.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        verification_id=verification.id,
        verification_token=verification.token,
        signature=email.SIGNATURE.format(domain=config.DOMAIN_NAME)
    )

    return send(
        'Welcome to osu!Titanic',
        message,
        user.email
    )

def send_password_reset_email(verification: DBVerification, user: DBUser):
    message = email.PASSWORD_RESET.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        verification_id=verification.id,
        verification_token=verification.token,
        signature=email.SIGNATURE.format(domain=config.DOMAIN_NAME)
    )

    return send(
        'Reset your password',
        message,
        user.email
    )

def send_password_changed_email(user: DBUser):
    message = email.PASSWORD_CHANGED.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        signature=email.SIGNATURE.format(domain=config.DOMAIN_NAME)
    )

    return send(
        'Your password was changed',
        message,
        user.email
    )

def send_email_changed(user: DBUser):
    message = email.EMAIL_CHANGED.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        signature=email.SIGNATURE.format(domain=config.DOMAIN_NAME)
    )

    return send(
        'Your email address was changed',
        message,
        user.email
    )

def send_reactivate_account_email(verification: DBVerification, user: DBUser):
    message = email.REACTIVATE_ACCOUNT.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        verification_id=verification.id,
        verification_token=verification.token,
        signature=email.SIGNATURE.format(domain=config.DOMAIN_NAME)
    )

    return send(
        'Reactivate your account',
        message,
        user.email
    )

def send_new_location_email(user: DBUser, country: str):
    message = email.NEW_LOCATION.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        country=country,
        signature=email.SIGNATURE.format(
            domain=config.DOMAIN_NAME
        )
    )

    return send(
        'New login from a new location',
        message,
        user.email
    )
