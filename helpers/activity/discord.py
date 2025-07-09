
from app.common.constants import UserActivity, DatabaseStatus
from app.common.database.repositories import wrapper
from app.common.database.objects import DBActivity
from sqlalchemy.orm import Session
from app.common.webhooks import *

import config
import app

def format_leaderboard_rank(activity: DBActivity) -> Embed:
    ...

def format_ranks_gained(activity: DBActivity) -> Embed:
    if activity.data["rank"] > 20:
        return

    embed = Embed(
        title='Climbing the ranks',
        description=(
            f'{activity.data["username"]} has risen {activity.data["ranks_gained"]} '
            f'rank{"s" if activity.data["ranks_gained"] != 1 else ""}, '
            f'now placed #{activity.data["rank"]} overall in {activity.data["mode"]}.'
        ),
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        thumbnail=Thumbnail(url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'),
        color=0x00ff00
    )
    return embed

def format_number_one(activity: DBActivity) -> Embed:
    embed = Embed(
        title='I can see the top',
        description=(
            f'{activity.data["username"]} has taken the lead as the top-ranked '
            f'{activity.data["mode"]} player.'
        ),
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        thumbnail=Thumbnail(url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'),
        color=0x00ff00
    )
    return embed

def format_pp_record(activity: DBActivity) -> Embed:
    embed = Embed(
        title=f'New pp record ({activity.data["mode"]})',
        description=(
            f'{activity.data["username"]} achieved a new pp record of **{activity.data["pp"]}pp** '
            f'on [{activity.data["beatmap"]}](http://osu.{config.DOMAIN_NAME}/b/{activity.data["beatmap_id"]})'
        ),
        thumbnail=Thumbnail(url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'),
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        color=0x00ff00
    )
    return embed

def format_beatmap_upload(activity: DBActivity) -> Embed:
    embed = Embed(title=activity.data["beatmapset_name"])
    embed.thumbnail = Thumbnail(url=f'http://osu.{config.DOMAIN_NAME}/mt/{activity.data["beatmapset_id"]}')
    embed.author = Author(
        name=f"{activity.data["username"]} uploaded a new beatmap!",
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    embed.color = 0x66c453
    embed.add_field(name="Title", value=activity.data["title"], inline=True)
    embed.add_field(name="Artist", value=activity.data["artist"], inline=True)
    embed.add_field(name="Creator", value=activity.data["username"], inline=True)
    embed.add_field(name="Link", value=f"http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}")
    return embed

def format_beatmap_revival(activity: DBActivity) -> Embed:
    embed = Embed(title=activity.data["beatmapset_name"])
    embed.thumbnail = Thumbnail(url=f'http://osu.{config.DOMAIN_NAME}/mt/{activity.data["beatmapset_id"]}')
    embed.url = f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}'
    embed.color = 0x23db32
    embed.author = Author(
        name=f"{activity.data["username"]} revived a beatmap!",
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    return embed

def format_beatmap_nomination(activity: DBActivity) -> Embed:
    author_text = {
        'add': f'{activity.data["username"]} nominated a Beatmap',
        'reset': f'{activity.data["username"]} reset all nominations',
    }
    color = {
        'add': 0x00da1d,
        'reset': 0xff0000,
    }
    embed = Embed(
        title=activity.data["beatmapset_name"],
        url=f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        thumbnail=Thumbnail(f'http://osu.{config.DOMAIN_NAME}/mt/{activity.data["beatmapset_id"]}'),
        color=color.get(activity.data["type"])
    )
    embed.author = Author(
        name=author_text.get(activity.data["type"]),
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    return embed

def format_beatmap_status_update(activity: DBActivity) -> Embed:
    embed = Embed(
        title=activity.data["beatmapset_name"],
        url=f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        thumbnail=Thumbnail(f'http://osu.{config.DOMAIN_NAME}/mt/{activity.data["beatmapset_id"]}'),
        color=0x009ed9
    )
    embed.author = Author(
        name=f'{activity.data["username"]} updated a beatmap',
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    embed.fields = [
        Field(
            version,
            f'{DatabaseStatus(status).name}',
            inline=True
        )
        for version, status in activity.data["beatmaps"].items()
    ]
    return embed

def format_beatmap_nuked(activity: DBActivity) -> Embed:
    embed = Embed(
        title=activity.data["beatmapset_name"],
        url=f'http://osu.{config.DOMAIN_NAME}/s/{activity.data["beatmapset_id"]}',
        thumbnail=Thumbnail(f'http://osu.{config.DOMAIN_NAME}/mt/{activity.data["beatmapset_id"]}'),
        color=0xff0000
    )
    embed.author = Author(
        name=f'{activity.data["username"]} nuked a Beatmap',
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    return embed

def format_topic_created(activity: DBActivity) -> Embed:
    embed = Embed(
        title=activity.data["topic_name"],
        description=activity.data["content"],
        url=f'http://osu.{config.DOMAIN_NAME}/forum/t/{activity.data["topic_id"]}',
        color=0xc4492e,
        thumbnail=(
            Image(f'https://osu.{config.DOMAIN_NAME}/{activity.data["topic_icon"]}')
            if activity.data["topic_icon"] else None
        )
    )
    embed.author = Author(
        name=f'{activity.data["username"]} created a new Topic',
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    return embed

def format_post_created(activity: DBActivity) -> Embed:
    embed = Embed(
        title=activity.data["topic_name"],
        description=activity.data["content"],
        url=f'http://osu.{config.DOMAIN_NAME}/forum/p/{activity.data["post_id"]}',
        color=0xc4492e,
        thumbnail=(
            Image(f'https://osu.{config.DOMAIN_NAME}/{activity.data["topic_icon"]}')
            if activity.data["topic_icon"] else None
        )
    )
    embed.author = Author(
        name=f'{activity.data["username"]} created a Post',
        url=f'http://osu.{config.DOMAIN_NAME}/u/{activity.user_id}',
        icon_url=f'http://osu.{config.DOMAIN_NAME}/a/{activity.user_id}'
    )
    return embed

formatters = {
    UserActivity.BeatmapLeaderboardRank.value: format_leaderboard_rank,
    UserActivity.RanksGained.value: format_ranks_gained,
    UserActivity.NumberOne.value: format_number_one,
    UserActivity.PPRecord.value: format_pp_record,
    UserActivity.BeatmapUploaded.value: format_beatmap_upload,
    UserActivity.BeatmapRevived.value: format_beatmap_revival,
    UserActivity.BeatmapStatusUpdated.value: format_beatmap_status_update,
    UserActivity.BeatmapNominated.value: format_beatmap_nomination,
    UserActivity.BeatmapNuked.value: format_beatmap_nuked,
    UserActivity.ForumTopicCreated.value: format_topic_created,
    UserActivity.ForumPostCreated.value: format_post_created
}
