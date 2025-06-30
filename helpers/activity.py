
from app.common.database.repositories import activities, wrapper
from app.common.constants import UserActivity, DatabaseStatus
from app.common.database.objects import DBActivity
from app.common import officer
from sqlalchemy.orm import Session

import config
import app

def on_submit_fail(e: Exception) -> None:
    officer.call(
        f'Failed to submit highlight: "{e}"',
        exc_info=e
    )

@wrapper.exception_wrapper(on_submit_fail)
def submit(
    user_id: int,
    mode: int | None,
    type: UserActivity,
    data: dict,
    session: Session,
    is_announcement: bool = False,
    is_hidden: bool = False
) -> None:
    app.session.events.submit(
        'bancho_event',
        user_id=user_id,
        mode=mode,
        type=type.value,
        data=data,
        is_announcement=is_announcement
    )

    if is_hidden:
        return

    activities.create(
        user_id, mode,
        type, data,
        session=session
    )

def format_ranks_gained(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )

    return (
        f'{user_link} has risen {activity.data["ranks_gained"]} '
        f'rank{"s" if activity.data["ranks_gained"] != 1 else ""}, '
        f'now placed #{activity.data["rank"]} overall in {activity.data["mode"]}.'
    )

def format_number_one(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )

    return (
        f'{user_link} has taken the lead as the top-ranked '
        f'{activity.data["mode"]} player.'
    )

def format_leaderboard_rank(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'http://osu.{config.DOMAIN_NAME}/b/{activity.data["beatmap_id"]}',
        escape_brackets=escape_brackets
    )
    data = dict(activity.data)

    return "".join([
        f'{user_link} achieved rank #{data["beatmap_rank"]} on {beatmap_link} ',
        (
            f'with {data["mods"]} '
            if data.get("mods") else ""
        ),
        f'<{data["mode"]}>',
        (
            f' ({data["pp"]}pp)'
            if data.get("pp") else ""
        )
    ])

def format_lost_first_place(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'http://osu.{config.DOMAIN_NAME}/b/{activity.data["beatmap_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{user_link} has lost first place on {beatmap_link} <{activity.data["mode"]}>'

def format_pp_record(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'http://osu.{config.DOMAIN_NAME}/b/{activity.data["beatmap_id"]}',
        escape_brackets=escape_brackets
    )

    return (
        f'{user_link} has set the new pp record on {beatmap_link} with'
        f' {activity.data["pp"]}pp <{activity.data["mode"]}>'
    )

def format_top_play(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'http://osu.{config.DOMAIN_NAME}/b/{activity.data["beatmap_id"]}',
        escape_brackets=escape_brackets
    )

    return (
        f'{user_link} got a new top play on {beatmap_link} with '
        f'{activity.data["pp"]}pp <{activity.data["mode"]}>'
    )

def format_achievement(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )

    return f'{user_link} unlocked an achievement: {activity.data["achievement"]}'

def format_beatmap_upload(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmapset_link = format_chat_link(
        activity.data['beatmapset_name'],
        f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{user_link} uploaded a new beatmapset "{beatmapset_link}"'

def format_beatmap_update(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmapset_link = format_chat_link(
        activity.data['beatmapset_name'],
        f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{user_link} has updated the beatmap "{beatmapset_link}"'

def format_beatmap_revival(activity: DBActivity, escape_brackets: bool = False) -> str:
    beatmapset_link = format_chat_link(
        activity.data['beatmapset_name'],
        f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{beatmapset_link} has been revived from eternal slumber.'

def format_topic_created(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    topic_link = format_chat_link(
        activity.data['topic_name'],
        f'http://osu.{config.DOMAIN_NAME}/forum/t/{activity.data["topic_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{user_link} created a new topic "{topic_link}"'

def format_beatmap_status_update(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmapset_link = format_chat_link(
        activity.data['beatmapset_name'],
        f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        escape_brackets=escape_brackets
    )
    status_name = DatabaseStatus(activity.data['status']).name

    return f'{beatmapset_link} was set to "{status_name}" by {user_link}'

def format_beatmap_nomination(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    beatmapset_link = format_chat_link(
        activity.data['beatmapset_name'],
        f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{beatmapset_link} was nominated by {user_link}'

def format_post_created(activity: DBActivity, escape_brackets: bool = False) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        escape_brackets=escape_brackets
    )
    post_link = format_chat_link(
        activity.data['topic_name'],
        f'http://osu.{config.DOMAIN_NAME}/forum/t/{activity.data["topic_id"]}/p/{activity.data["post_id"]}',
        escape_brackets=escape_brackets
    )

    return f'{user_link} created a post in "{post_link}"'

def format_chat_link(key: str, value: str, escape_brackets: bool = False) -> str:
    if escape_brackets:
        key = key.replace('(', '&#40;').replace(')', '&#41;') \
                 .replace('[', '&#91;').replace(']', '&#93;')

        value = value.replace('(', '&#40;').replace(')', '&#41;') \
                     .replace('[', '&#91;').replace(']', '&#93;')

    return f'[{value} {key}]'

formatters = {
    UserActivity.RanksGained.value: format_ranks_gained,
    UserActivity.NumberOne.value: format_number_one,
    UserActivity.BeatmapLeaderboardRank.value: format_leaderboard_rank,
    UserActivity.LostFirstPlace.value: format_lost_first_place,
    UserActivity.PPRecord.value: format_pp_record,
    UserActivity.TopPlay.value: format_top_play,
    UserActivity.AchievementUnlocked.value: format_achievement,
    UserActivity.BeatmapUploaded.value: format_beatmap_upload,
    UserActivity.BeatmapUpdated.value: format_beatmap_update,
    UserActivity.BeatmapRevived.value: format_beatmap_revival,
    UserActivity.BeatmapStatusUpdated.value: format_beatmap_status_update,
    UserActivity.BeatmapNominated.value: format_beatmap_nomination,
    UserActivity.ForumTopicCreated.value: format_topic_created,
    UserActivity.ForumPostCreated.value: format_post_created
}
