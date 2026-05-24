# config.py — loads config.json and exposes values as module-level names.
# All other modules import from here; the JSON file is the source of truth.

import json
from pathlib import Path

_cfg_path = Path(__file__).parent / "config.json"
with _cfg_path.open() as _f:
    _c = json.load(_f)

# --- Screen ---
SCREEN_WIDTH  = _c["screen"]["width"]
SCREEN_HEIGHT = _c["screen"]["height"]
FPS           = _c["screen"]["fps"]

# --- Colors (JSON arrays → tuples) ---
def _rgb(key): return tuple(_c["colors"][key])

BLACK         = _rgb("black")
WHITE         = _rgb("white")
RED_BRIGHT    = _rgb("red_bright")
RED_DIM       = _rgb("red_dim")
GREEN_BRIGHT  = _rgb("green_bright")
GREEN_DIM     = _rgb("green_dim")
YELLOW_BRIGHT = _rgb("yellow_bright")
YELLOW_DIM    = _rgb("yellow_dim")
GRAY          = _rgb("gray")
DARK_GRAY     = _rgb("dark_gray")
CLOCK_COLOR   = _rgb("clock_color")
DELTA_COLOR   = _rgb("delta_color")

# --- Font sizes ---
SCORE_FONT_SIZE = _c["fonts"]["score_size"]
CLOCK_FONT_SIZE = _c["fonts"]["clock_size"]
DELTA_FONT_SIZE = _c["fonts"]["delta_size"]

# --- Layout fractions ---
SCORE_Y_FRAC       = _c["layout"]["score_y_frac"]
LEFT_SCORE_X_FRAC  = _c["layout"]["left_score_x_frac"]
RIGHT_SCORE_X_FRAC = _c["layout"]["right_score_x_frac"]
CLOCK_X_FRAC       = _c["layout"]["clock_x_frac"]
CLOCK_Y_FRAC       = _c["layout"]["clock_y_frac"]
DELTA_Y_FRAC       = _c["layout"]["delta_y_frac"]
INDICATOR_W_FRAC   = _c["layout"]["indicator_w_frac"]
INDICATOR_H_FRAC   = _c["layout"]["indicator_h_frac"]
INDICATOR_Y_FRAC   = _c["layout"]["indicator_y_frac"]
PIE_RADIUS         = _c["layout"]["pie_radius"]
PIE_CENTER_Y_FRAC  = _c["layout"]["pie_center_y_frac"]

# --- Game ---
BOUT_WIN_SCORE        = _c["game"]["bout_win_score"]
WINNER_RESET_DELAY_MS = _c["game"]["winner_reset_delay_ms"]

# --- Timing ---
HIT_WINDOW_MS             = _c["timing"]["hit_window_ms"]
HIT_INDICATOR_DURATION_MS = _c["timing"]["hit_indicator_duration_ms"]
DELTA_DISPLAY_MS          = _c["timing"]["delta_display_ms"]
DISCONNECT_HIT_COUNT      = _c["timing"]["disconnect_hit_count"]
DISCONNECT_WINDOW_MS      = _c["timing"]["disconnect_window_ms"]
DISCONNECT_SILENCE_MS     = _c["timing"]["disconnect_silence_ms"]

# --- Serial defaults ---
DEFAULT_PORT = _c["serial"]["default_port"]
DEFAULT_BAUD = _c["serial"]["default_baud"]

# --- Audio ---
MIXER_BUFFER         = _c["audio"]["mixer_buffer"]
SOUND_HIT_ON_TARGET  = _c["audio"]["hit_on_target_file"]
SOUND_HIT_OFF_TARGET = _c["audio"]["hit_off_target_file"]
SOUND_RESET          = _c["audio"]["reset_file"]
SOUND_WINNER_LEFT    = _c["audio"]["winner_left_file"]
SOUND_WINNER_RIGHT   = _c["audio"]["winner_right_file"]
SOUND_POINT_LEFT     = _c["audio"]["point_left_file"]
SOUND_POINT_RIGHT    = _c["audio"]["point_right_file"]

# Tone settings used when WAV files are absent
TONE_HIT_ON_TARGET  = _c["audio"]["tones"]["hit_on_target"]
TONE_HIT_OFF_TARGET = _c["audio"]["tones"]["hit_off_target"]
TONE_RESET          = _c["audio"]["tones"]["reset"]
TONE_WINNER         = _c["audio"]["tones"]["winner"]
TONE_POINT          = _c["audio"]["tones"]["point"]
