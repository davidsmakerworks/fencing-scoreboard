# audio.py — sound loading and playback helpers

import os
import pygame
import config


def _generate_tone(frequency: int, duration_ms: int, volume: float = 0.6) -> pygame.mixer.Sound:
    """Synthesise a single sine-wave tone."""
    import numpy as np
    sample_rate = 44100
    n_samples   = int(sample_rate * duration_ms / 1000)
    t           = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
    wave        = (np.sin(2 * np.pi * frequency * t) * volume * 32767).astype(np.int16)
    stereo = np.column_stack([wave, wave])
    return pygame.sndarray.make_sound(stereo)


def _generate_sequence(notes: list, repeats: int = 1, volume: float = 0.6) -> pygame.mixer.Sound:
    """
    Synthesise a multi-note sequence as a single Sound buffer.
    Each entry in *notes* is {"frequency": Hz, "duration_ms": ms}.
    frequency=0 produces silence.  The whole pattern is repeated *repeats* times.
    """
    import numpy as np
    sample_rate = 44100
    buffers = []
    for _ in range(repeats):
        for note in notes:
            freq   = note["frequency"]
            dur_ms = note["duration_ms"]
            n      = int(sample_rate * dur_ms / 1000)
            if freq == 0:
                buffers.append(np.zeros(n, dtype=np.int16))
            else:
                t    = np.linspace(0, dur_ms / 1000, n, endpoint=False)
                wave = (np.sin(2 * np.pi * freq * t) * volume * 32767).astype(np.int16)
                buffers.append(wave)
    full   = np.concatenate(buffers)
    stereo = np.column_stack([full, full])
    return pygame.sndarray.make_sound(stereo)


def _load_or_generate(path: str, frequency: int, duration_ms: int) -> pygame.mixer.Sound:
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return _generate_tone(frequency, duration_ms)


def _load_or_generate_sequence(path: str, notes: list, repeats: int = 1) -> pygame.mixer.Sound:
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return _generate_sequence(notes, repeats)


class AudioManager:
    def __init__(self):
        # pygame.mixer must already be initialised by the time this is called
        self.hit_on_target  = _load_or_generate(config.SOUND_HIT_ON_TARGET,
                                                 config.TONE_HIT_ON_TARGET["frequency"],
                                                 config.TONE_HIT_ON_TARGET["duration_ms"])
        self.hit_off_target = _load_or_generate(config.SOUND_HIT_OFF_TARGET,
                                                 config.TONE_HIT_OFF_TARGET["frequency"],
                                                 config.TONE_HIT_OFF_TARGET["duration_ms"])
        self.reset          = _load_or_generate(config.SOUND_RESET,
                                                 config.TONE_RESET["frequency"],
                                                 config.TONE_RESET["duration_ms"])
        self.winner_left  = _load_or_generate_sequence(config.SOUND_WINNER_LEFT,
                                                        config.TONE_WINNER["notes"],
                                                        config.TONE_WINNER["repeats"])
        self.winner_right = _load_or_generate_sequence(config.SOUND_WINNER_RIGHT,
                                                        config.TONE_WINNER["notes"],
                                                        config.TONE_WINNER["repeats"])
        self.point_left   = _load_or_generate_sequence(config.SOUND_POINT_LEFT,
                                                        config.TONE_POINT["notes"])
        self.point_right  = _load_or_generate_sequence(config.SOUND_POINT_RIGHT,
                                                        config.TONE_POINT["notes"])

    def play_hit_on_target(self):
        self.hit_on_target.play()

    def play_hit_off_target(self):
        self.hit_off_target.play()

    def play_reset(self):
        self.reset.play()

    def play_winner_left(self):
        self.winner_left.play()

    def play_winner_right(self):
        self.winner_right.play()

    def play_point_left(self):
        self.point_left.play()

    def play_point_right(self):
        self.point_right.play()
