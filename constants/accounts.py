
from enum import IntEnum

class TokenSource(IntEnum):
    Web = 0
    Api = 1
    OAuth2 = 2

class ScopeSensitivity(IntEnum):
    Public = 0
    Low = 1
    Medium = 2
    High = 3
    Staff = 4

ScopeDefinitions: dict[str, tuple[str, ScopeSensitivity]] = {
    'users.profile.view': (
        'Identify and read your public profile',
        ScopeSensitivity.Public,
    ),
    'users.profile.update': (
        'Update your profile information',
        ScopeSensitivity.Medium,
    ),
    'users.friends.view': (
        'View your friends list',
        ScopeSensitivity.Low
    ),
    'users.friends.create': (
        'Add friends',
        ScopeSensitivity.Low
    ),
    'users.friends.delete': (
        'Remove friends',
        ScopeSensitivity.Low
    ),
    'users.irc.view_token': (
        'Read your IRC authentication token',
        ScopeSensitivity.High,
    ),
    'users.irc.regenerate_token': (
        'Regenerate your IRC authentication token',
        ScopeSensitivity.High,
    ),
    'users.notifications.view': (
        'Read your notifications',
        ScopeSensitivity.Low,
    ),
    'users.notifications.delete': (
        'Delete your notifications',
        ScopeSensitivity.Low,
    ),
    'beatmaps.collaborations.update': (
        'Update collaborators and roles on your beatmaps',
        ScopeSensitivity.Medium,
    ),
    'beatmaps.collaborations.delete': (
        'Remove collaborators from your beatmaps',
        ScopeSensitivity.Medium,
    ),
    'beatmaps.collaborations.view_requests': (
        'View collaboration requests on your beatmaps',
        ScopeSensitivity.Low,
    ),
    'beatmaps.collaborations.create_request': (
        'Request collaboration on a beatmap',
        ScopeSensitivity.Low,
    ),
    'beatmaps.collaborations.delete_request': (
        'Withdraw or delete a collaboration request',
        ScopeSensitivity.Low,
    ),
    'beatmaps.collaborations.accept_request': (
        'Accept a collaboration request',
        ScopeSensitivity.Low,
    ),
    'beatmaps.revive': (
        'Revive a previously deleted or archived beatmap',
        ScopeSensitivity.Low,
    ),
    'beatmaps.update_description': (
        'Update beatmap descriptions',
        ScopeSensitivity.Low
    ),
    'beatmaps.delete': (
        'Delete your beatmaps',
        ScopeSensitivity.High,
    ),
    'beatmaps.favourites.create': (
        'Add beatmaps to your favourites',
        ScopeSensitivity.Low,
    ),
    'beatmaps.favourites.delete': (
        'Remove beatmaps from your favourites',
        ScopeSensitivity.Low,
    ),
    'scores.pins.create': (
        'Pin scores to your profile',
        ScopeSensitivity.Low,
    ),
    'scores.pins.delete': (
        'Unpin scores from your profile',
        ScopeSensitivity.Low,
    ),
    'forum.kudosu.reward': (
        'Award kudosu to a post',
        ScopeSensitivity.Medium,
    ),
    'forum.kudosu.revoke': (
        'Revoke kudosu from a post',
        ScopeSensitivity.Medium,
    ),
    'forum.kudosu.reset': (
        'Reset kudosu on a post',
        ScopeSensitivity.Medium,
    ),
    'bancho.events.view': (
        'Read real-time Bancho events',
        ScopeSensitivity.Public,
    ),
    'beatmaps.download': (
        'Download beatmap files',
        ScopeSensitivity.Public,
    ),
    'forum.bookmarks.view': (
        'View your forum bookmarks',
        ScopeSensitivity.Low,
    ),
    'forum.bookmarks.create': (
        'Bookmark forum topics',
        ScopeSensitivity.Low,
    ),
    'forum.bookmarks.delete': (
        'Remove forum bookmarks',
        ScopeSensitivity.Low,
    ),
    'forum.subscriptions.view': (
        'View your topic subscriptions',
        ScopeSensitivity.Low,
    ),
    'forum.subscriptions.create': (
        'Subscribe to topics',
        ScopeSensitivity.Low,
    ),
    'forum.subscriptions.delete': (
        'Unsubscribe from topics',
        ScopeSensitivity.Low,
    ),
    'forum.topics.create': (
        'Create new forum topics',
        ScopeSensitivity.High,
    ),
    'forum.topics.create_beatmap': (
        'Create topics in beatmap forums',
        ScopeSensitivity.Staff,
    ),
    'forum.topics.edit': (
        'Edit forum topics',
        ScopeSensitivity.High,
    ),
    'forum.topics.edit_icon': (
        'Edit topic icons where allowed by the forum',
        ScopeSensitivity.Staff,
    ),
    'forum.topics.link_beatmapset': (
        'Link and unlink beatmapsets from forum topics',
        ScopeSensitivity.Staff,
    ),
    'forum.posts.create': (
        'Create new forum posts',
        ScopeSensitivity.High,
    ),
    'forum.posts.delete': (
        'Delete your forum posts',
        ScopeSensitivity.High,
    ),
    'forum.posts.edit': (
        'Edit your forum posts',
        ScopeSensitivity.High,
    ),
    'forum.moderation.topics.edit_icon': (
        'Edit topic icons regardless of forum settings',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.topics.lock': (
        'Lock and unlock forum topics',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.topics.set_options': (
        'Set forum topic visibility options',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.topics.set_status': (
        'Set forum topic status text',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.topics.bypass_lock': (
        'Post or edit through locked topics',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.posts.edit': (
        "Edit other users' forum posts",
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.posts.delete': (
        "Delete other users' forum posts",
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.posts.lock': (
        'Lock and unlock forum posts',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.posts.bypass_lock': (
        'Edit locked forum posts',
        ScopeSensitivity.Staff,
    ),
    'forum.moderation.posts.bypass_length': (
        'Bypass forum post length limits',
        ScopeSensitivity.Staff,
    ),
    'chat.messages.view': (
        'Read public chat messages',
        ScopeSensitivity.Public,
    ),
    'chat.messages.private.view': (
        'Read your private messages',
        ScopeSensitivity.Medium,
    ),
    'chat.messages.create': (
        'Send messages in public chats',
        ScopeSensitivity.High,
    ),
    'chat.messages.private.create': (
        'Send private messages',
        ScopeSensitivity.High,
    ),
    'beatmaps.update_status': (
        'Update beatmap status',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.metadata.update': (
        'Update beatmap metadata',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.nominations.create': (
        'Nominate beatmaps',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.nominations.delete': (
        'Reset beatmap nominations',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.nuke': (
        'Force-delete beatmaps',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.resources.mp3.upload': (
        'Upload mp3 audio preview files',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.resources.mt.upload': (
        'Upload beatmap thumbnail files',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.resources.osu.upload': (
        'Upload .osu files',
        ScopeSensitivity.Staff,
    ),
    'beatmaps.resources.osz.upload': (
        'Upload .osz files',
        ScopeSensitivity.Staff,
    ),
}
