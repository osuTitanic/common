
from enum import IntFlag, IntEnum

class Playstyle(IntFlag):
    NotSpecified = 0
    Mouse = 1
    Tablet = 2
    Keyboard = 4
    Touch = 8

class UserActivity(IntEnum):
    RanksGained = 1
    NumberOne = 2
    BeatmapLeaderboardRank = 3
    LostFirstPlace = 4
    PPRecord = 5
    TopPlay = 6
    AchievementUnlocked = 7
    ScoreSubmitted = 8
    BeatmapUploaded = 9
    BeatmapUpdated = 10
    BeatmapRevived = 11
    BeatmapFavouriteAdded = 12
    BeatmapFavouriteRemoved = 13
    BeatmapRated = 14
    BeatmapCommented = 15
    BeatmapDownloaded = 16
    BeatmapStatusUpdated = 17
    BeatmapNominated = 18
    ForumTopicCreated = 19
    ForumPostCreated = 20
    ForumSubscribed = 21
    ForumUnsubscribed = 22
    ForumBookmarked = 23
    ForumUnbookmarked = 24
    OsuCoinsReceived = 25
    OsuCoinsUsed = 26
    FriendAdded = 27
    FriendRemoved = 28
    ReplayWatched = 29
    ScreenshotUploaded = 30
    UserRegistration = 31
    UserLogin = 32
    UserChatMessage = 33
    UserMatchCreated = 34
    UserMatchJoined = 35
    UserMatchLeft = 36
