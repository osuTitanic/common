
from dataclasses import dataclass
from typing import List, Optional

from ..constants import ButtonState, ReplayAction, GameMode

import hashlib

@dataclass
class ScoreFrame:
    time: int
    id: int
    c300: int
    c100: int
    c50: int
    cGeki: int
    cKatu: int
    cMiss: int
    total_score: int
    max_combo: int
    current_combo: int
    perfect: bool
    hp: int
    tag_byte: int = 0

    @property
    def checksum(self) -> str:
        return hashlib.md5(''.join([
            str(self.time),
            'false', # "pass" ?
            str(self.c300),
            str(self.c50),
            str(self.cGeki),
            str(self.cKatu),
            str(self.cMiss),
            str(self.current_combo),
            str(self.max_combo),
            str(self.hp),
        ]).encode()).hexdigest()

    def total_hits(self, mode: GameMode) -> int:
        if mode == GameMode.CatchTheBeat:
            return self.c50 + self.c100 + self.c300 + self.cMiss + self.cKatu

        elif mode == GameMode.OsuMania:
            return self.c300 + self.c100 + self.c50 + self.cGeki + self.cKatu + self.cMiss

        return self.c50 + self.c100 + self.c300 + self.cMiss

    def accuracy(self, mode: GameMode) -> float:
        if self.total_hits(mode) == 0:
            return 0.0

        if mode == GameMode.Osu:
            return (
                ((self.c300 * 300.0) + (self.c100 * 100.0) + (self.c50 * 50.0))
                / (self.total_hits(mode) * 300.0)
            )

        elif mode == GameMode.Taiko:
            return ((self.c100 * 0.5) + self.c300) / self.total_hits(mode)

        elif mode == GameMode.CatchTheBeat:
            return (self.c300 + self.c100 + self.c50) / self.total_hits(mode)

        elif mode == GameMode.OsuMania:
            return  (
                        (
                          (self.c50 * 50.0) + (self.c100 * 100.0) + (self.cKatu * 200.0) + ((self.c300 + self.cGeki) * 300.0)
                        )
                        / (self.total_hits(mode) * 300.0)
                    )

        else:
            return 0.0

@dataclass
class ReplayFrame:
    button_state: ButtonState
    taiko_byte: int
    mouse_x: float
    mouse_y: float
    time: int

@dataclass
class ReplayFrameBundle:
    extra: int
    action: ReplayAction
    frames: List[ReplayFrame]
    score_frame: Optional[ScoreFrame] = None
