# audio.py — sound loading and playback helpers

import os
import pygame
import config


def _generate_tone(frequency: int, duration_ms: int, volume: float = 0.6) -> pygame.mixer.Sound:
    """Synthesise a simple sine-wave tone when a WAV file is not present."""
    import numpy as np
    sample_rate = 44100
    n_samples   = int(sample_rate * duration_ms / 1000)
    t           = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
    wave        = (np.sin(2 * np.pi * frequency * t) * volume * 32767).astype(np.int16)
    # Pygame expects a 2-D array for stereo; duplicate the channel
    stereo = np.column_stack([wave, wave])
    sound  = pygame.sndarray.make_sound(stereo)
    return sound


def _load_or_generate(path: str, frequency: int, duration_ms: int) -> pygame.mixer.Sound:
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return _generate_tone(frequency, duration_ms)


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

    def play_hit_on_target(self):
        self.hit_on_target.play()

    def play_hit_off_target(self):
        self.hit_off_target.play()

    def play_reset(self):
        self.reset.play()
