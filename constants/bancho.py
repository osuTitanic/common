
from enum import IntEnum, IntFlag

class ClientStatus(IntEnum):
    Idle         = 0
    Afk          = 1
    Playing      = 2
    Editing      = 3
    Modding      = 4
    Multiplayer  = 5
    Watching     = 6
    Unknown      = 7
    Testing      = 8
    Submitting   = 9
    Paused       = 10
    Lobby        = 11
    Multiplaying = 12
    OsuDirect    = 13

class ButtonState(IntFlag):
    NoButton = 0
    Left1    = 1
    Right1   = 2
    Left2    = 4
    Right2   = 8
    Smoke    = 16
