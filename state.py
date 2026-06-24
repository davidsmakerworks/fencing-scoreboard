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
    delta_ms:        Optional[int]  = None   # None = not shown
    delta_set_time:  Optional[int]  = None   # ticks when delta was last set
    delta_first_left: Optional[bool] = None  # True = left hit first, False = right, None = simultaneous

    # Clock
    clock_running:   bool  = False
    clock_seconds:   float = 180.0   # counts down

    # Bout winner — set to the ticks at which scores should auto-reset after a win
    winner_reset_at: Optional[int] = None

    # Runtime score limit (in-memory only; initialised from config on startup)
    bout_win_score: int = 5

    # Set when the countdown clock reaches zero; cleared only by a clock reset.
    # While True, all hit signals are ignored.
    time_expired: bool = False

    # Set by the start sequence; the main loop starts the clock when now_ms reaches this value.
    start_clock_at: Optional[int] = None

    # Transient status message displayed centred at the bottom of the screen
    status_message: Optional[str] = None
    status_message_until: Optional[int] = None

    # Set when the serial reader thread encounters an unrecoverable error
    serial_failed: bool = False
    serial_error_msg: Optional[str] = None

    def reset_scores(self):
        self.score_left      = 0
        self.score_right     = 0
        self.winner_reset_at = None

    def reset_indicators(self):
        self.hit_window_start   = None
        self.hit_left_active    = False
        self.hit_right_active   = False
        self.white_left_active  = False
        self.white_right_active = False
        self.delta_ms            = None
        self.delta_set_time      = None
        self.delta_first_left    = None
        self.winner_reset_at    = None
