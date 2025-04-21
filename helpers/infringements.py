
from ..database.objects import DBUser
from ..cache import leaderboards
from .. import officer

from ..database.repositories import (
    infringements,
    clients,
    wrapper,
    scores,
    groups,
    users,
    stats
)

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

@wrapper.session_wrapper
def silence_user(
    user: DBUser,
    duration: int,
    reason: str | None = None,
    session: Session | None = None
) -> datetime:
    if user.silence_end:
        user.silence_end += timedelta(seconds=duration)
    else:
        user.silence_end = datetime.now() + timedelta(seconds=duration)

    users.update(
        user.id,
        {'silence_end': user.silence_end},
        session=session
    )

    # Add entry inside infringements table
    infringements.create(
        user.id,
        action=1,
        length=(datetime.now() + timedelta(seconds=duration)),
        description=reason,
        session=session
    )

    officer.call(
        f'{user.name} was silenced for {duration} seconds. '
        f'Reason: "{reason}"'
    )

    return user.silence_end

@wrapper.session_wrapper
def unsilence_user(
    user: DBUser,
    session: Session | None = None
) -> None:
    users.update(
        user.id,
        {'silence_end': None},
        session=session
    )

    # Delete infringements from website
    infringement = infringements.fetch_recent_by_action(
        user.id,
        action=1,
        session=session
    )

    if infringement:
        infringements.delete_by_id(
            infringement.id,
            session=session
        )

    officer.call(
        f'{user.name} was unsilenced.'
    )

@wrapper.session_wrapper
def restrict_user(
    user: DBUser,
    reason: str | None = None,
    until: datetime | None = None,
    autoban: bool = False,
    session: Session | None = None
) -> None:
    user.restricted = True

    # Update user
    users.update(
        user.id,
        {'restricted': True},
        session=session
    )

    # Remove from leaderboards
    leaderboards.remove(
        user.id,
        user.country
    )

    scores.hide_all(user.id, session=session)
    stats.update_all(user.id, {'rank': 0}, session=session)

    groups.delete_entry(user.id, 999, session=session)
    groups.delete_entry(user.id, 1000, session=session)

    # Update hardware
    clients.update_all(user.id, {'banned': True}, session=session)

    # Add entry inside infringements table
    infringements.create(
        user.id,
        action=0,
        length=until,
        description=reason,
        is_permanent=True if not until else False,
        session=session
    )

    officer.call(
        f'{user.name} was {"auto-" if autoban else ""}restricted. '
        f'Reason: "{reason}"'
    )

@wrapper.session_wrapper
def unrestrict_user(
    user: DBUser,
    restore_scores: bool = False,
    session: Session | None = None
) -> None:
    users.update(user.id, {'restricted': False}, session=session)

    # Add to user & supporter group
    groups.create_entry(user.id, 999, session=session)
    groups.create_entry(user.id, 1000, session=session)

    # Update hardware
    clients.update_all(user.id, {'banned': False}, session=session)

    if not restore_scores:
        stats.delete_all(user.id)
        leaderboards.remove(user.id, user.country, session=session)
    else:
        scores.restore_hidden_scores(user.id, session=session)

    for user_stats in stats.fetch_all(user.id):
        leaderboards.update(
            user_stats,
            user.country
        )

    officer.call(f'Player "{user.name}" was unrestricted.')
