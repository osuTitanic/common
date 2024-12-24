
from __future__ import annotations

from .database.objects import DBVerification, DBUser
from .constants import email
from . import officer

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from email.mime.text import MIMEText
from smtplib import SMTP

import config
import app

client = SendGridAPIClient(config.SENDGRID_API_KEY)

def smtp(subject: str, message: str, email: str):
    with SMTP(config.SMTP_HOST, config.SMTP_PORT) as smtp:
        msg = MIMEText(message, 'plain')
        msg['Subject'] = subject
        msg['From'] = config.EMAIL_SENDER
        msg['To'] = email

        required_extensions = [
            'starttls',
            'auth'
        ]

        for extension in required_extensions:
            if smtp.has_extn(extension):
                continue

            app.session.logger.warning(
                f'Failed to send email: '
                f'SMTP server does not support {extension}'
            )
            return

        try:
            smtp.starttls()
            smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.sendmail(config.EMAIL_SENDER, [email], msg.as_string())
        except Exception as e:
            app.session.logger.warning(f'Failed to send email: {e}')
            officer.call(f'Failed to send email to {email} with subject "{subject}": {e}')

def sendgrid(subject: str, message: str, email: str):
    message = Mail(
        from_email=config.EMAIL_SENDER,
        to_emails=email,
        subject=subject,
        html_content=message.replace('\n', '<br>')
    )

    response = client.send(message)

    if response.status_code != 200:
        app.session.logger.warning(
            f'Failed to send email: {response.body}'
        )
        officer.call(
            f'Failed to send email to {email} with subject "{subject}": '
            f'{response.body} ({response.status_code})'
        )

    return response

def mailgun(subject: str, message: str, email: str):
    response = app.session.requests.post(
        f'https://{config.MAILGUN_URL}/v3/{config.EMAIL_DOMAIN}/messages',
        auth=('api', config.MAILGUN_API_KEY),
        data={
            'from': f'Titanic <{config.EMAIL_SENDER}>',
            'to': [email],
            'subject': subject,
            'html': message.replace('\n', '<br>')
        }
    )

    if not response.ok:
        app.session.logger.warning(
            f'Failed to send email: {response.text}'
        )
        officer.call(
            f'Failed to send email to {email} with subject "{subject}": '
            f'{response.text} ({response.status_code})'
        )

    return response

def send(subject: str, message: str, email: str):
    app.session.logger.info(f'Sending email to {email} with subject "{subject}"...')

    if not config.EMAILS_ENABLED:
        app.session.logger.warning(f'Failed to send email: Emails are disabled.')
        return

    providers = {
        'sendgrid': sendgrid,
        'mailgun': mailgun,
        'smtp': smtp
    }

    if not config.EMAIL_PROVIDER in providers:
        app.session.logger.warning(f'Failed to send email: Invalid email provider ({config.EMAIL_PROVIDER}).')
        return
    
    return providers[config.EMAIL_PROVIDER](subject, message, email)

def send_welcome_email(verification: DBVerification, user: DBUser):
    message = email.WELCOME.format(
        domain=config.DOMAIN_NAME,
        username=user.name,
        verification_id=verification.id,
        verification_token=verification.token,
        signature=email.SIGNATURE.format(domain=config.DOMAIN_NAME)
    )

    return send(
        'Welcome to Titanic!',
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
