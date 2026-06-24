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

# --- Fonts (names list + size; bold optional, defaults False) ---
SCORE_FONT_NAMES = _c["fonts"]["score"]["names"]
SCORE_FONT_SIZE  = _c["fonts"]["score"]["size"]
SCORE_FONT_BOLD  = _c["fonts"]["score"].get("bold", False)

CLOCK_FONT_NAMES = _c["fonts"]["clock"]["names"]
CLOCK_FONT_SIZE  = _c["fonts"]["clock"]["size"]
CLOCK_FONT_BOLD  = _c["fonts"]["clock"].get("bold", False)

DELTA_FONT_NAMES = _c["fonts"]["delta"]["names"]
DELTA_FONT_SIZE  = _c["fonts"]["delta"]["size"]
DELTA_FONT_BOLD  = _c["fonts"]["delta"].get("bold", False)

STATUS_FONT_NAMES = _c["fonts"]["status"]["names"]
STATUS_FONT_SIZE  = _c["fonts"]["status"]["size"]
STATUS_FONT_BOLD  = _c["fonts"]["status"].get("bold", False)

# --- Layout fractions ---
SCORE_Y_FRAC       = _c["layout"]["score_y_frac"]
LEFT_SCORE_X_FRAC  = _c["layout"]["left_score_x_frac"]
RIGHT_SCORE_X_FRAC = _c["layout"]["right_score_x_frac"]
CLOCK_X_FRAC       = _c["layout"]["clock_x_frac"]
CLOCK_Y_FRAC       = _c["layout"]["clock_y_frac"]
DELTA_Y_FRAC       = _c["layout"]["delta_y_frac"]
INDICATOR_W_FRAC        = _c["layout"]["indicator_w_frac"]
INDICATOR_H_FRAC        = _c["layout"]["indicator_h_frac"]
INDICATOR_Y_FRAC        = _c["layout"]["indicator_y_frac"]
INDICATOR_OUTLINE_WIDTH = _c["layout"]["indicator_outline_width"]
PIE_RADIUS         = _c["layout"]["pie_radius"]
PIE_CENTER_Y_FRAC  = _c["layout"]["pie_center_y_frac"]

# --- Game ---
BOUT_WIN_SCORE        = _c["game"]["bout_win_score"]
WINNER_RESET_DELAY_MS = _c["game"]["winner_reset_delay_ms"]

# --- Gamepad buttons ---
GAMEPAD_SCORE_LIMIT_BUTTON    = _c["gamepad"]["score_limit_button"]
GAMEPAD_RESET_BUTTON          = _c["gamepad"]["reset_button"]
GAMEPAD_CLOCK_TOGGLE_BUTTON   = _c["gamepad"]["clock_toggle_button"]
GAMEPAD_START_SEQUENCE_BUTTON = _c["gamepad"]["start_sequence_button"]

# --- Start sequence timing ---
START_SEQUENCE_INITIAL_DELAY_MS = _c["start_sequence"]["initial_delay_ms"]
START_SEQUENCE_RANDOM_MIN_MS    = _c["start_sequence"]["random_delay_min_ms"]
START_SEQUENCE_RANDOM_MAX_MS    = _c["start_sequence"]["random_delay_max_ms"]

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
DISABLE_VOICE        = _c["audio"]["disable_voice"]
MIXER_BUFFER         = _c["audio"]["mixer_buffer"]
SOUND_HIT_ON_TARGET  = _c["audio"]["hit_on_target_file"]
SOUND_HIT_OFF_TARGET = _c["audio"]["hit_off_target_file"]
SOUND_RESET          = _c["audio"]["reset_file"]
SOUND_TOUCH_LEFT     = _c["audio"]["touch_left_file"]
SOUND_TOUCH_RIGHT    = _c["audio"]["touch_right_file"]
SOUND_HALT           = _c["audio"]["halt_file"]
SOUND_TIME_EXPIRED   = _c["audio"]["time_expired_file"]
SOUND_EN_GARDE       = _c["audio"]["en_garde_file"]
SOUND_READY          = _c["audio"]["ready_file"]
SOUND_FENCE          = _c["audio"]["fence_file"]

# Tone fallbacks when WAV files are absent
TONE_HIT_ON_TARGET  = _c["audio"]["tones"]["hit_on_target"]
TONE_HIT_OFF_TARGET = _c["audio"]["tones"]["hit_off_target"]
TONE_RESET          = _c["audio"]["tones"]["reset"]
TONE_TOUCH           = _c["audio"]["tones"]["touch"]
TONE_HALT_BEEPS      = _c["audio"]["tones"]["halt_beeps"]
TONE_VICTORY_FANFARE = _c["audio"]["tones"]["victory_fanfare"]

# Announcement speech-cadence gaps (ms)
ANNOUNCE_GAP_AFTER_TOUCH       = _c["audio"]["announcement"]["gap_after_touch_ms"]
ANNOUNCE_GAP_BETWEEN_WORDS     = _c["audio"]["announcement"]["gap_between_words_ms"]
ANNOUNCE_GAP_BETWEEN_SCORES    = _c["audio"]["announcement"]["gap_between_scores_ms"]
ANNOUNCE_GAP_SCORE_TO_ALL      = _c["audio"]["announcement"]["gap_score_to_all_ms"]
ANNOUNCE_GAP_AFTER_WINNER_NAME = _c["audio"]["announcement"]["gap_after_winner_name_ms"]
