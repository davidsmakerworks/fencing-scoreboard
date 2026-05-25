# display.py — all rendering logic; stateless given a BoutState + current time

import math
import pygame
import config
from state import BoutState


# ---------------------------------------------------------------------------
# Font cache — loaded once after pygame.init()
# ---------------------------------------------------------------------------
_fonts: dict = {}

# Rendered text surface cache — keyed by (font_name, text, color).
# font.render() is expensive on a software-rendered Pi; we only call it when
# the content actually changes.
_text_cache: dict = {}


def load_fonts():
    """Call once after pygame.init() to populate the font cache."""
    _fonts["score"]  = pygame.font.SysFont("Arial", config.SCORE_FONT_SIZE, bold=True)
    _fonts["clock"]  = pygame.font.SysFont("Arial", config.CLOCK_FONT_SIZE, bold=True)
    _fonts["delta"]  = pygame.font.SysFont("Arial", config.DELTA_FONT_SIZE)
    _fonts["status"] = pygame.font.SysFont("Arial", config.DELTA_FONT_SIZE)


def _render_cached(font_key: str, text: str, color) -> pygame.Surface:
    key = (font_key, text, color)
    if key not in _text_cache:
        _text_cache[key] = _fonts[font_key].render(text, True, color)
    return _text_cache[key]


# ---------------------------------------------------------------------------
# Helper: scale a fraction-based coordinate to actual pixels
# ---------------------------------------------------------------------------
def _px(frac_x: float, frac_y: float, w: int, h: int) -> tuple[int, int]:
    return int(frac_x * w), int(frac_y * h)


# ---------------------------------------------------------------------------
# Individual drawing helpers
# ---------------------------------------------------------------------------

def _draw_score(surface: pygame.Surface, score: int, x: int, y: int, color):
    text = _render_cached("score", str(score), color)
    rect = text.get_rect(center=(x, y))
    surface.blit(text, rect)


def _draw_clock(surface: pygame.Surface, seconds: float, running: bool, x: int, y: int):
    total = max(0, int(seconds))
    mm, ss = divmod(total, 60)

    colon_color = config.YELLOW_BRIGHT if running else config.CLOCK_COLOR

    min_surf   = _render_cached("clock", str(mm),     config.CLOCK_COLOR)
    colon_surf = _render_cached("clock", ":",          colon_color)
    sec_surf   = _render_cached("clock", f"{ss:02d}", config.CLOCK_COLOR)

    total_w = min_surf.get_width() + colon_surf.get_width() + sec_surf.get_width()
    left    = x - total_w // 2
    top_min   = y - min_surf.get_height()   // 2
    top_colon = y - colon_surf.get_height() // 2
    top_sec   = y - sec_surf.get_height()   // 2

    surface.blit(min_surf,   (left, top_min))
    left += min_surf.get_width()
    surface.blit(colon_surf, (left, top_colon))
    left += colon_surf.get_width()
    surface.blit(sec_surf,   (left, top_sec))


def _draw_delta(surface: pygame.Surface, delta_ms: int, first_left,
                cx: int, y: int, w: int, h: int):
    """Draw the Δt label, millisecond value, pie-chart circle, and first-hit arrow."""
    # Text
    label = _render_cached("delta", f"Δt  {delta_ms} ms", config.DELTA_COLOR)
    rect  = label.get_rect(center=(cx, y))
    surface.blit(label, rect)

    # Pie chart — centered below the delta text, shifted down by half a radius
    pie_cx = cx
    pie_cy = int(config.PIE_CENTER_Y_FRAC * h) + config.PIE_RADIUS // 2
    r      = config.PIE_RADIUS
    frac   = min(delta_ms / config.HIT_WINDOW_MS, 1.0)

    # Background circle
    pygame.draw.circle(surface, config.DARK_GRAY, (pie_cx, pie_cy), r)
    pygame.draw.circle(surface, config.GRAY, (pie_cx, pie_cy), r, 2)

    if frac > 0:
        # pygame.draw.arc uses start/stop in radians measured CCW from 3 o'clock.
        # We want CW from 12 o'clock, so: start = π/2 − angle, stop = π/2
        angle_rad = frac * 2 * math.pi
        # Fill wedge with a polygon
        steps  = max(3, int(angle_rad * r))
        points = [(pie_cx, pie_cy)]
        for i in range(steps + 1):
            a = math.pi / 2 - (angle_rad * i / steps)
            points.append((
                pie_cx + r * math.cos(a),
                pie_cy - r * math.sin(a),
            ))
        if len(points) >= 3:
            pygame.draw.polygon(surface, config.DELTA_COLOR, points)
        # Redraw outline on top
        pygame.draw.circle(surface, config.GRAY, (pie_cx, pie_cy), r, 2)

    # Arrow below pie indicating which fencer hit first (suppressed for simultaneous hits)
    if first_left is not None and delta_ms > 0:
        arrow_hw  = r // 2        # half-width of arrow base
        arrow_hh  = r // 3        # half-height of arrow base
        arrow_gap = 10
        arrow_cy  = pie_cy + r + arrow_gap + arrow_hh
        if first_left:
            color  = config.RED_BRIGHT
            points = [
                (pie_cx - arrow_hw, arrow_cy),            # tip (left)
                (pie_cx + arrow_hw, arrow_cy - arrow_hh), # top-right
                (pie_cx + arrow_hw, arrow_cy + arrow_hh), # bottom-right
            ]
        else:
            color  = config.GREEN_BRIGHT
            points = [
                (pie_cx + arrow_hw, arrow_cy),            # tip (right)
                (pie_cx - arrow_hw, arrow_cy - arrow_hh), # top-left
                (pie_cx - arrow_hw, arrow_cy + arrow_hh), # bottom-left
            ]
        pygame.draw.polygon(surface, color, points)


def _draw_indicator_bar(surface: pygame.Surface, cx: int, cy: int, w: int, h: int,
                        color, filled: bool):
    rect       = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    line_width = 0 if filled else config.INDICATOR_OUTLINE_WIDTH
    pygame.draw.rect(surface, color, rect, line_width, border_radius=8)


def _draw_indicators(surface: pygame.Surface, state: BoutState, now_ms: int, sw: int, sh: int):
    bar_w = int(config.INDICATOR_W_FRAC * sw)
    bar_h = int(config.INDICATOR_H_FRAC * sh)
    ind_y = int(config.INDICATOR_Y_FRAC * sh)

    left_cx  = int(config.LEFT_SCORE_X_FRAC  * sw)
    right_cx = int(config.RIGHT_SCORE_X_FRAC * sw)

    # On-target bars — both sides share a single window; they extinguish together
    window_open   = (state.hit_window_start is not None and
                     (now_ms - state.hit_window_start) < config.HIT_INDICATOR_DURATION_MS)
    left_on_lit   = window_open and state.hit_left_active
    right_on_lit  = window_open and state.hit_right_active
    left_on_color  = config.RED_BRIGHT   if left_on_lit  else config.RED_DIM
    right_on_color = config.GREEN_BRIGHT if right_on_lit else config.GREEN_DIM
    _draw_indicator_bar(surface, left_cx,  ind_y, bar_w, bar_h, left_on_color,  filled=left_on_lit)
    _draw_indicator_bar(surface, right_cx, ind_y, bar_w, bar_h, right_on_color, filled=right_on_lit)

    # Off-target bars — share the same window; extinguish simultaneously with on-target bars
    white_y = ind_y - bar_h - 10
    left_white_lit  = window_open and state.white_left_active
    right_white_lit = window_open and state.white_right_active
    left_white_color  = config.YELLOW_BRIGHT if left_white_lit  else config.YELLOW_DIM
    right_white_color = config.YELLOW_BRIGHT if right_white_lit else config.YELLOW_DIM
    _draw_indicator_bar(surface, left_cx,  white_y, bar_w, bar_h // 2, left_white_color,  filled=left_white_lit)
    _draw_indicator_bar(surface, right_cx, white_y, bar_w, bar_h // 2, right_white_color, filled=right_white_lit)


def _draw_status_message(surface: pygame.Surface, message: str, sw: int, sh: int):
    surf = _render_cached("status", message, config.WHITE)
    rect = surf.get_rect(centerx=sw // 2, bottom=sh - 20)
    surface.blit(surf, rect)


# ---------------------------------------------------------------------------
# Public render function
# ---------------------------------------------------------------------------

def render(surface: pygame.Surface, state: BoutState, now_ms: int):
    sw, sh = surface.get_size()
    surface.fill(config.BLACK)

    score_y  = int(config.SCORE_Y_FRAC      * sh)
    left_cx  = int(config.LEFT_SCORE_X_FRAC * sw)
    right_cx = int(config.RIGHT_SCORE_X_FRAC * sw)

    _draw_score(surface, state.score_left,  left_cx,  score_y, config.RED_BRIGHT)
    _draw_score(surface, state.score_right, right_cx, score_y, config.GREEN_BRIGHT)

    # Clock
    clock_x, clock_y = _px(config.CLOCK_X_FRAC, config.CLOCK_Y_FRAC, sw, sh)
    _draw_clock(surface, state.clock_seconds, state.clock_running, clock_x, clock_y)

    # Delta + pie chart (only when data is present)
    if state.delta_ms is not None:
        delta_y = int(config.DELTA_Y_FRAC * sh)
        _draw_delta(surface, state.delta_ms, state.delta_first_left, clock_x, delta_y, sw, sh)

    # Hit indicator bars
    _draw_indicators(surface, state, now_ms, sw, sh)

    # Transient status message (e.g. score limit change)
    if state.status_message is not None:
        _draw_status_message(surface, state.status_message, sw, sh)
