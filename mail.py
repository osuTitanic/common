
from .database.objects import DBVerification, DBUser
from .constants import email

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import config

client = SendGridAPIClient(config.SENDGRID_API_KEY)

def send(subject: str, message: str, email: str):
    message = Mail(
        from_email=config.SENDGRID_EMAIL,
        to_emails=email,
        subject=subject,
        html_content=message.replace('\n', '<br>')
    )

    return client.send(message)

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
