# stats.py — persistent hit-interval history, stored in stats.json

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

_STATS_PATH = Path(__file__).parent / "stats.json"

# Each list keeps at most this many entries; the oldest is dropped first.
MAX_INTERVALS = 100


def load() -> tuple[list, list]:
    """Return (red_intervals, green_intervals) from stats.json, or empty lists."""
    try:
        with _STATS_PATH.open() as f:
            data = json.load(f)
        red   = [int(v) for v in data.get("red_intervals",   [])][-MAX_INTERVALS:]
        green = [int(v) for v in data.get("green_intervals", [])][-MAX_INTERVALS:]
        return red, green
    except FileNotFoundError:
        return [], []
    except (OSError, ValueError, TypeError) as exc:
        log.warning("Could not read %s (%s) — starting with empty stats", _STATS_PATH, exc)
        return [], []


def save(red_intervals: list, green_intervals: list):
    try:
        with _STATS_PATH.open("w") as f:
            json.dump({"red_intervals":   red_intervals,
                       "green_intervals": green_intervals}, f)
    except OSError as exc:
        log.warning("Could not write %s: %s", _STATS_PATH, exc)
