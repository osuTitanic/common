
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
    BeatmapUploaded = 8
    BeatmapRevived = 9
    ForumTopicCreated = 10
    ForumPostCreated = 11
