# audio.py — sound loading, tone generation, and announcement scheduling

import os
import random
import logging
from pathlib import Path
import pygame
import config

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Low-level generation helpers
# ---------------------------------------------------------------------------

def _generate_tone(frequency: int, duration_ms: int, volume: float = 0.6) -> pygame.mixer.Sound:
    """Synthesise a mono sine-wave tone (pygame upmixes to both speakers at playback)."""
    import numpy as np
    sample_rate = 44100
    n_samples   = int(sample_rate * duration_ms / 1000)
    t           = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
    wave        = (np.sin(2 * np.pi * frequency * t) * volume * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([wave, wave]))


def _generate_sequence(notes: list, repeats: int = 1, volume: float = 0.6) -> pygame.mixer.Sound:
    """
    Synthesise a mono multi-note sequence as a single Sound buffer.
    Each note: {"frequency": Hz, "duration_ms": ms}. frequency=0 = silence.
    """
    import numpy as np
    sample_rate = 44100
    buffers = []
    for _ in range(repeats):
        for note in notes:
            freq, dur_ms = note["frequency"], note["duration_ms"]
            n = int(sample_rate * dur_ms / 1000)
            if freq == 0:
                buffers.append(np.zeros(n, dtype=np.int16))
            else:
                t    = np.linspace(0, dur_ms / 1000, n, endpoint=False)
                wave = (np.sin(2 * np.pi * freq * t) * volume * 32767).astype(np.int16)
                buffers.append(wave)
    mono = np.concatenate(buffers)
    return pygame.sndarray.make_sound(np.column_stack([mono, mono]))


def _load_or_generate(path: str, frequency: int, duration_ms: int) -> pygame.mixer.Sound:
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return _generate_tone(frequency, duration_ms)


def _load_or_generate_sequence(path: str, notes: list, repeats: int = 1) -> pygame.mixer.Sound:
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return _generate_sequence(notes, repeats)


def _load_optional(path: str) -> pygame.mixer.Sound | None:
    """Load a Sound if the file exists; log a warning and return None otherwise."""
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    log.warning("Announcement sound not found (item will be skipped): %s", path)
    return None


def _voice_optional(path: str) -> pygame.mixer.Sound | None:
    """Like _load_optional, but returns None immediately when disable_voice is set."""
    if config.DISABLE_VOICE:
        return None
    return _load_optional(path)


def _voice_or_generate_sequence(path: str, notes: list, repeats: int = 1) -> pygame.mixer.Sound:
    """Like _load_or_generate_sequence, but forces tone generation when disable_voice is set."""
    if config.DISABLE_VOICE:
        return _generate_sequence(notes, repeats)
    return _load_or_generate_sequence(path, notes, repeats)


# ---------------------------------------------------------------------------
# AudioManager
# ---------------------------------------------------------------------------

# Spoken number words for scores 0-15
_NUMBER_WORDS = [
    "zero", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
]


class AudioManager:
    def __init__(self):
        # pygame.mixer must already be initialised

        # --- Immediate-play sounds (hit signals, reset) ---
        self.hit_on_target  = _load_or_generate(config.SOUND_HIT_ON_TARGET,
                                                 config.TONE_HIT_ON_TARGET["frequency"],
                                                 config.TONE_HIT_ON_TARGET["duration_ms"])
        self.hit_off_target = _load_or_generate(config.SOUND_HIT_OFF_TARGET,
                                                 config.TONE_HIT_OFF_TARGET["frequency"],
                                                 config.TONE_HIT_OFF_TARGET["duration_ms"])
        self.reset_sound    = _load_or_generate(config.SOUND_RESET,
                                                 config.TONE_RESET["frequency"],
                                                 config.TONE_RESET["duration_ms"])

        # --- Announcement phrase sounds ---
        _sd = Path(config.SOUND_HIT_ON_TARGET).parent  # derives the sounds/ directory

        def _p(name: str) -> str:
            return str(_sd / f"{name}.wav")

        # Touch calls — voice WAV if present and not disabled, otherwise synthesised tone
        self._touch_left  = _voice_or_generate_sequence(config.SOUND_TOUCH_LEFT,
                                                         config.TONE_TOUCH["notes"])
        self._touch_right = _voice_or_generate_sequence(config.SOUND_TOUCH_RIGHT,
                                                         config.TONE_TOUCH["notes"])

        # Halt: voice WAV if present and not disabled, otherwise synthesised beeps
        self._halt = _voice_or_generate_sequence(config.SOUND_HALT,
                                                  config.TONE_HALT_BEEPS["notes"],
                                                  config.TONE_HALT_BEEPS["repeats"])

        # Remaining items are pure voice — all silenced when disable_voice is set
        self._time_expired_sound = _voice_optional(config.SOUND_TIME_EXPIRED)

        self._en_garde = _voice_optional(config.SOUND_EN_GARDE)
        self._ready    = _voice_optional(config.SOUND_READY)
        self._fence    = _voice_optional(config.SOUND_FENCE)

        self._the_score_is       = _voice_optional(_p("the_score_is"))
        self._the_final_score_is = _voice_optional(_p("the_final_score_is"))
        self._the_winner_is      = _voice_optional(_p("the_winner_is"))
        self._fencer_left        = _voice_optional(_p("the_fencer_to_my_left"))
        self._fencer_right       = _voice_optional(_p("the_fencer_to_my_right"))
        self._all                = _voice_optional(_p("all"))

        self._numbers: dict[int, pygame.mixer.Sound | None] = {
            i: _voice_optional(_p(word)) for i, word in enumerate(_NUMBER_WORDS)
        }

        # Victory fanfare — always synthesised; only enqueued when disable_voice is set
        self._victory_fanfare = _generate_sequence(config.TONE_VICTORY_FANFARE["notes"])

        # Announcement queue: list of (play_at_ms, Sound), sorted by play_at_ms
        self._queue: list[tuple[float, pygame.mixer.Sound]] = []

    # ------------------------------------------------------------------
    # Immediate-play methods
    # ------------------------------------------------------------------

    def play_hit_on_target(self):
        self.hit_on_target.play()

    def play_hit_off_target(self):
        self.hit_off_target.play()

    def play_reset(self):
        self.reset_sound.play()

    # ------------------------------------------------------------------
    # Announcement scheduling
    # ------------------------------------------------------------------

    def _dur(self, sound: pygame.mixer.Sound | None) -> float:
        """Duration in ms, or 0 if sound is None."""
        return sound.get_length() * 1000.0 if sound is not None else 0.0

    def _enqueue(self, t: float, sound: pygame.mixer.Sound | None) -> float:
        """Append sound to the queue at time t; return t advanced by its duration."""
        if sound is not None:
            self._queue.append((t, sound))
            return t + self._dur(sound)
        return t

    def _build_score_suffix(self, t: float, scorer_score: int, other_score: int) -> float:
        """Append 'X' or 'X all' or 'X Y' to the queue. Returns advanced time."""
        scorer_snd = self._numbers.get(scorer_score)
        other_snd  = self._numbers.get(other_score)

        t = self._enqueue(t, scorer_snd)
        if scorer_score == other_score:
            t += config.ANNOUNCE_GAP_SCORE_TO_ALL
            t = self._enqueue(t, self._all)
        else:
            t += config.ANNOUNCE_GAP_BETWEEN_SCORES
            t = self._enqueue(t, other_snd)
        return t

    def schedule_point_announcement(self, scorer_is_left: bool,
                                    scorer_score: int, other_score: int,
                                    now_ms: int) -> None:
        """
        Queue: touch call → pause → "the score is" → score (with "all" if tied).
        Cancels any in-progress announcement.
        """
        self._queue.clear()
        t = float(now_ms)

        touch = self._touch_left if scorer_is_left else self._touch_right
        t = self._enqueue(t, touch)
        t += config.ANNOUNCE_GAP_AFTER_TOUCH

        t = self._enqueue(t, self._the_score_is)
        t += config.ANNOUNCE_GAP_BETWEEN_WORDS

        self._build_score_suffix(t, scorer_score, other_score)

    def schedule_winner_announcement(self, winner_is_left: bool,
                                     winner_score: int, loser_score: int,
                                     now_ms: int) -> int:
        """
        Voice mode:  touch call → "the winner is" → fencer name → "the final score is" → score.
        Tone mode:   touch call → victory fanfare.
        Returns the suggested winner_reset_at timestamp (ms) — after the last sound
        plus a 1-second buffer.
        """
        self._queue.clear()
        t = float(now_ms)

        touch = self._touch_left if winner_is_left else self._touch_right
        t = self._enqueue(t, touch)

        if config.DISABLE_VOICE:
            t += config.ANNOUNCE_GAP_BETWEEN_WORDS
            t = self._enqueue(t, self._victory_fanfare)
            t += 1000.0
            return int(t)

        t += config.ANNOUNCE_GAP_AFTER_TOUCH

        t = self._enqueue(t, self._the_winner_is)
        t += config.ANNOUNCE_GAP_BETWEEN_WORDS

        fencer = self._fencer_left if winner_is_left else self._fencer_right
        t = self._enqueue(t, fencer)
        t += config.ANNOUNCE_GAP_AFTER_WINNER_NAME

        t = self._enqueue(t, self._the_final_score_is)
        t += config.ANNOUNCE_GAP_BETWEEN_WORDS

        t = self._build_score_suffix(t, winner_score, loser_score)
        t += 1000.0  # 1-second buffer after last word

        return int(t)

    def cancel_queue(self):
        """Discard all pending queued announcements."""
        self._queue.clear()

    def schedule_start_sequence(self, now_ms: int, initial_delay_ms: int,
                                 random_min_ms: int, random_max_ms: int) -> int:
        """
        Queue: (initial delay) → "en garde" → (random delay) → "ready" →
               (random delay) → "fence" → [clock starts].
        Cancels any in-progress announcements.
        Returns the timestamp (ms) at which the clock should start.
        """
        self._queue.clear()
        t = float(now_ms) + initial_delay_ms

        t = self._enqueue(t, self._en_garde)
        t += random.randint(random_min_ms, random_max_ms)

        t = self._enqueue(t, self._ready)
        t += random.randint(random_min_ms, random_max_ms)

        t = self._enqueue(t, self._fence)
        # t is now the moment "fence" finishes — clock starts then
        return int(t)

    def schedule_time_expired_announcement(self, left_score: int, right_score: int,
                                            now_ms: int) -> int:
        """
        Voice mode: halt → time-expired phrase → winner announcement (or tie score).
        Tone mode:  halt → victory fanfare (winner) or halt only (tie).
        Winner is determined by the higher score regardless of bout_win_score.
        Returns the suggested winner_reset_at timestamp (ms).
        """
        self._queue.clear()
        t = float(now_ms)

        t = self._enqueue(t, self._halt)

        if config.DISABLE_VOICE:
            if left_score != right_score:
                t += config.ANNOUNCE_GAP_BETWEEN_WORDS
                t = self._enqueue(t, self._victory_fanfare)
            t += 1000.0
            return int(t)

        t += config.ANNOUNCE_GAP_BETWEEN_WORDS

        t = self._enqueue(t, self._time_expired_sound)
        t += config.ANNOUNCE_GAP_AFTER_TOUCH

        if left_score > right_score:
            t = self._enqueue(t, self._the_winner_is)
            t += config.ANNOUNCE_GAP_BETWEEN_WORDS
            t = self._enqueue(t, self._fencer_left)
            t += config.ANNOUNCE_GAP_AFTER_WINNER_NAME
            t = self._enqueue(t, self._the_final_score_is)
            t += config.ANNOUNCE_GAP_BETWEEN_WORDS
            t = self._build_score_suffix(t, left_score, right_score)
        elif right_score > left_score:
            t = self._enqueue(t, self._the_winner_is)
            t += config.ANNOUNCE_GAP_BETWEEN_WORDS
            t = self._enqueue(t, self._fencer_right)
            t += config.ANNOUNCE_GAP_AFTER_WINNER_NAME
            t = self._enqueue(t, self._the_final_score_is)
            t += config.ANNOUNCE_GAP_BETWEEN_WORDS
            t = self._build_score_suffix(t, right_score, left_score)
        else:
            # Tie — "The score is X all"
            t = self._enqueue(t, self._the_score_is)
            t += config.ANNOUNCE_GAP_BETWEEN_WORDS
            t = self._build_score_suffix(t, left_score, right_score)

        t += 1000.0
        return int(t)

    def update_announcements(self, now_ms: int) -> None:
        """Play any queued announcement items that are due. Call once per main-loop frame."""
        while self._queue and now_ms >= self._queue[0][0]:
            _, sound = self._queue.pop(0)
            sound.play()
