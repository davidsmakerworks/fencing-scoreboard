# state.py — BoutState dataclass; single source of truth for all scoreboard state

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BoutState:
    # Scores
    score_left:  int = 0
    score_right: int = 0

    # On-target hit indicators.
    # hit_window_start is set by the FIRST hit in an exchange and never updated
    # by subsequent hits; both sides extinguish simultaneously when the window expires.
    hit_window_start: Optional[int] = None   # ticks of first hit; None = no active window
    hit_left_active:  bool = False            # left on-target indicator is lit
    hit_right_active: bool = False            # right on-target indicator is lit

    # Off-target indicators — share the same window as on-target hits
    white_left_active:  bool = False
    white_right_active: bool = False

    # Double-hit delta
    delta_ms: Optional[int] = None   # None = not shown

    # Clock
    clock_running:   bool  = False
    clock_seconds:   float = 180.0   # counts down

    def reset_scores(self):
        self.score_left  = 0
        self.score_right = 0

    def reset_indicators(self):
        self.hit_window_start  = None
        self.hit_left_active   = False
        self.hit_right_active  = False
        self.white_left_active  = False
        self.white_right_active = False
        self.delta_ms          = None
