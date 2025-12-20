

from enum import IntFlag

class Mods(IntFlag):
    NoMod       = 0
    NoFail      = 1 << 0
    Easy        = 1 << 1
    NoVideo     = 1 << 2
    Hidden      = 1 << 3
    HardRock    = 1 << 4
    SuddenDeath = 1 << 5
    DoubleTime  = 1 << 6
    Relax       = 1 << 7
    HalfTime    = 1 << 8
    Nightcore   = 1 << 9
    Flashlight  = 1 << 10
    Autoplay    = 1 << 11
    SpunOut     = 1 << 12
    Autopilot   = 1 << 13
    Perfect     = 1 << 14
    Key4        = 1 << 15
    Key5        = 1 << 16
    Key6        = 1 << 17
    Key7        = 1 << 18
    Key8        = 1 << 19
    FadeIn      = 1 << 20
    Random      = 1 << 21
    Cinema      = 1 << 22
    Target      = 1 << 23
    Key9        = 1 << 24
    KeyCoop     = 1 << 25
    Key1        = 1 << 26
    Key3        = 1 << 27
    Key2        = 1 << 28
    ScoreV2     = 1 << 29
    Mirror      = 1 << 30

    KeyMod = Key1 | Key2 | Key3 | Key4 | Key5 | Key6 | Key7 | Key8 | Key9 | KeyCoop
    FreeModAllowed = NoFail | Easy | Hidden | HardRock | SuddenDeath | Flashlight | FadeIn | Relax | Autopilot | SpunOut | KeyMod
    SpeedMods = DoubleTime | HalfTime| Nightcore

    @property
    def members(self) -> list:
        return [flag for flag in Mods if self & flag]

    @property
    def short(self) -> str:
        if not self:
            return "NM"

        return ''.join([
            ModMapping[mod]
            for mod in self.members
        ])

    @classmethod
    def from_string(cls, mod_string: str):
        mod_string = mod_string.replace(",", "").replace(" ", "")
        mods = Mods.NoMod

        # Parse mods into their short forms
        parsed_mods = [
            mod_string[idx : idx + 2].upper()
            for idx in range(0, len(mod_string), 2)
        ]

        for mod in parsed_mods:
            if not (m := StringMapping.get(mod)):
                continue

            mods |= m

        return mods

StringMapping = {
    "NM": Mods.NoMod,
    "NF": Mods.NoFail,
    "EZ": Mods.Easy,
    "NV": Mods.NoVideo,
    "HD": Mods.Hidden,
    "HR": Mods.HardRock,
    "SD": Mods.SuddenDeath,
    "DT": Mods.DoubleTime,
    "RX": Mods.Relax,
    "HT": Mods.HalfTime,
    "NC": Mods.Nightcore,
    "FL": Mods.Flashlight,
    "AT": Mods.Autoplay,
    "SO": Mods.SpunOut,
    "AP": Mods.Autopilot,
    "PF": Mods.Perfect,
    "K4": Mods.Key4,
    "K5": Mods.Key5,
    "K6": Mods.Key6,
    "K7": Mods.Key7,
    "K8": Mods.Key8,
    "FI": Mods.FadeIn,
    "RD": Mods.Random,
    "CN": Mods.Cinema,
    "TP": Mods.Target,
    "K9": Mods.Key9,
    "CP": Mods.KeyCoop,
    "K1": Mods.Key1,
    "K3": Mods.Key3,
    "K2": Mods.Key2,
    "SV2": Mods.ScoreV2,
    "MR": Mods.Mirror
}

ModMapping = {
    Mods.NoMod: "NM",
    Mods.NoFail: "NF",
    Mods.Easy: "EZ",
    Mods.NoVideo: "NV",
    Mods.Hidden: "HD",
    Mods.HardRock: "HR",
    Mods.SuddenDeath: "SD",
    Mods.DoubleTime: "DT",
    Mods.Relax: "RX",
    Mods.HalfTime: "HT",
    Mods.Nightcore: "NC",
    Mods.Flashlight: "FL",
    Mods.Autoplay: "AT",
    Mods.SpunOut: "SO",
    Mods.Autopilot: "AP",
    Mods.Perfect: "PF",
    Mods.Key4: "K4",
    Mods.Key5: "K5",
    Mods.Key6: "K6",
    Mods.Key7: "K7",
    Mods.Key8: "K8",
    Mods.FadeIn: "FI",
    Mods.Random: "RD",
    Mods.Cinema: "CN",
    Mods.Target: "TP",
    Mods.Key9: "K9",
    Mods.KeyCoop: "CP",
    Mods.Key1: "K1",
    Mods.Key3: "K3",
    Mods.Key2: "K2",
    Mods.ScoreV2: "SV2",
    Mods.Mirror: "MR",
    Mods.SpeedMods: "",
    Mods.KeyMod: "",
    Mods.FreeModAllowed: ""
}
