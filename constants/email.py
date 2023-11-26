
SIGNATURE = """osu!Titanic | https://osu.{domain}"""

WELCOME = """\
Welcome on board, {username}!

You've just taken your first steps to experience osu!'s early days.
Before you can play you need to activate your account, by clicking the link below.

https://osu.{domain}/account/verification?id={verification_id}&token={verification_token}

See you in game!

--
{signature}
"""

NEW_LOCATION = """\
Hi {username},

We have noticed that your account was accessed from a new device in {country}.
If that was not you, please REPLY IMMEDIATELY and RESET YOUR PASSWORD, as your account may be in danger.

You can reset your password here: https://osu.{domain}/account/settings#password

--
{signature}
"""

PASSWORD_RESET = """\
Hi {username},

You are receiving this notification because you have (or someone pretending to be you has) requested a new password be sent for your account on.
If you did not request this notification, then please ignore it. If you keep receiving it, please contact an administrator.

To use the new password, you need to activate it by clicking the link provided below.

https://osu.{domain}/account/verification?id={verification_id}&token={verification_token}&type=password

--
{signature}
"""

PASSWORD_CHANGED = """\
Hi {username},

You are receiving this notification because your account password was changed.
If that was not you, please REPLY IMMEDIATELY and RESET YOUR PASSWORD, as your account may be in danger.

You can reset your password here: https://osu.{domain}/account/settings#password

--
{signature}
"""

EMAIL_CHANGED = """\
Hi {username},

You are receiving this notification because you (or someone else) changed the email of your account.
If that was not you, please REPLY IMMEDIATELY, as your account may be in danger.

--
{signature}
"""

REACTIVATE_ACCOUNT = """\
Hi {username},

Your account was deactivated, because you have changed your email address.
In order to play again, you will have to re-activate your account, by clicking the link below.

https://osu.{domain}/account/verification?id={verification_id}&token={verification_token}

If that was not you, please ignore this email.

--
{signature}
"""
