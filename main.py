# main.py — entry point: arg parsing, Pygame init, main loop, state mutation

import argparse
import queue
import sys
import logging
import pygame

import config
import opcodes
import display
import audio
from state import BoutState
from serial_reader import start_serial_reader

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Demo / simulate mode key bindings
# ---------------------------------------------------------------------------
DEMO_KEYS = {
    pygame.K_q: (opcodes.OP_SCORE_LEFT_INC,  None),
    pygame.K_a: (opcodes.OP_SCORE_LEFT_DEC,  None),
    pygame.K_e: (opcodes.OP_SCORE_RIGHT_INC, None),
    pygame.K_d: (opcodes.OP_SCORE_RIGHT_DEC, None),
    pygame.K_r: (opcodes.OP_SCORE_RESET,     None),
    pygame.K_z: (opcodes.OP_HIT_LEFT,        None),
    pygame.K_x: (opcodes.OP_HIT_RIGHT,       None),
    pygame.K_c: (opcodes.OP_HIT_BOTH,        None),
    pygame.K_1: (opcodes.OP_WHITE_LEFT,       None),
    pygame.K_2: (opcodes.OP_WHITE_RIGHT,      None),
    pygame.K_3: (opcodes.OP_DELTA_TIME,       83),   # 83 ms example
    pygame.K_s: (opcodes.OP_CLOCK_START,      None),
    pygame.K_t: (opcodes.OP_CLOCK_STOP,       None),
    pygame.K_g: (opcodes.OP_CLOCK_RESET,      None),
    pygame.K_v: (opcodes.OP_CLOCK_SET,        180),  # 3:00
}


# ---------------------------------------------------------------------------
# Disconnect detection
# ---------------------------------------------------------------------------

class DisconnectDetector:
    """
    Suppresses the buzzer when hit signals arrive too rapidly (disconnected foil).

    Mutes audio once DISCONNECT_HIT_COUNT signals are seen within
    DISCONNECT_WINDOW_MS.  Unmutes after DISCONNECT_SILENCE_MS passes with no
    hit signals from either fencer.  Visuals are never affected.
    """

    def __init__(self):
        self._hit_times: list[int] = []
        self.muted = False

    def record_hit(self, now_ms: int):
        """Call on every hit-type opcode after deciding whether to play sound."""
        self._hit_times.append(now_ms)
        cutoff = now_ms - config.DISCONNECT_WINDOW_MS
        self._hit_times = [t for t in self._hit_times if t >= cutoff]
        if len(self._hit_times) >= config.DISCONNECT_HIT_COUNT:
            if not self.muted:
                log.warning("Disconnect detected — buzzer muted")
            self.muted = True

    def update(self, now_ms: int):
        """Call once per main-loop iteration to check whether silence has elapsed."""
        if self.muted and self._hit_times:
            if (now_ms - self._hit_times[-1]) >= config.DISCONNECT_SILENCE_MS:
                self.muted = False
                self._hit_times.clear()
                log.info("Disconnect cleared — buzzer restored")


# ---------------------------------------------------------------------------
# State mutation — called from the main loop only
# ---------------------------------------------------------------------------

def _window_active(state: BoutState, now_ms: int) -> bool:
    """True if the hit display window started by the first hit has not yet expired."""
    return (state.hit_window_start is not None and
            (now_ms - state.hit_window_start) < config.HIT_INDICATOR_DURATION_MS)


def _open_hit_window(state: BoutState, now_ms: int):
    """Start a fresh hit window and clear all indicator flags (called on the first hit)."""
    state.hit_window_start  = now_ms
    state.hit_left_active   = False
    state.hit_right_active  = False
    state.white_left_active  = False
    state.white_right_active = False


def apply_command(opcode: int, payload, state: BoutState,
                  audio_mgr: audio.AudioManager, detector: DisconnectDetector, now_ms: int):
    if opcode == opcodes.OP_SCORE_LEFT_INC:
        state.score_left = max(0, state.score_left + 1)
        if state.score_left == config.BOUT_WIN_SCORE:
            audio_mgr.play_winner_left()
            state.winner_reset_at = now_ms + config.WINNER_RESET_DELAY_MS
        else:
            audio_mgr.play_point_left()
    elif opcode == opcodes.OP_SCORE_LEFT_DEC:
        state.score_left  = max(0, state.score_left  - 1)
    elif opcode == opcodes.OP_SCORE_RIGHT_INC:
        state.score_right = max(0, state.score_right + 1)
        if state.score_right == config.BOUT_WIN_SCORE:
            audio_mgr.play_winner_right()
            state.winner_reset_at = now_ms + config.WINNER_RESET_DELAY_MS
        else:
            audio_mgr.play_point_right()
    elif opcode == opcodes.OP_SCORE_RIGHT_DEC:
        state.score_right = max(0, state.score_right - 1)
    elif opcode == opcodes.OP_SCORE_RESET:
        state.reset_scores()
        state.reset_indicators()
        audio_mgr.play_reset()

    elif opcode == opcodes.OP_HIT_LEFT:
        first_hit = not _window_active(state, now_ms)
        if first_hit:
            _open_hit_window(state, now_ms)
        state.hit_left_active = True
        if first_hit and not detector.muted:
            audio_mgr.play_hit_on_target()
        detector.record_hit(now_ms)

    elif opcode == opcodes.OP_HIT_RIGHT:
        first_hit = not _window_active(state, now_ms)
        if first_hit:
            _open_hit_window(state, now_ms)
        state.hit_right_active = True
        if first_hit and not detector.muted:
            audio_mgr.play_hit_on_target()
        detector.record_hit(now_ms)

    elif opcode == opcodes.OP_HIT_BOTH:
        first_hit = not _window_active(state, now_ms)
        if first_hit:
            _open_hit_window(state, now_ms)
        state.hit_left_active  = True
        state.hit_right_active = True
        if first_hit and not detector.muted:
            audio_mgr.play_hit_on_target()
        detector.record_hit(now_ms)

    elif opcode == opcodes.OP_WHITE_LEFT:
        first_hit = not _window_active(state, now_ms)
        if first_hit:
            _open_hit_window(state, now_ms)
        state.white_left_active = True
        if first_hit and not detector.muted:
            audio_mgr.play_hit_off_target()
        detector.record_hit(now_ms)

    elif opcode == opcodes.OP_WHITE_RIGHT:
        first_hit = not _window_active(state, now_ms)
        if first_hit:
            _open_hit_window(state, now_ms)
        state.white_right_active = True
        if first_hit and not detector.muted:
            audio_mgr.play_hit_off_target()
        detector.record_hit(now_ms)

    elif opcode == opcodes.OP_DELTA_TIME:
        state.delta_ms       = payload
        state.delta_set_time = now_ms

    elif opcode == opcodes.OP_CLOCK_START:
        state.clock_running = True
    elif opcode == opcodes.OP_CLOCK_STOP:
        state.clock_running = False
    elif opcode == opcodes.OP_CLOCK_RESET:
        state.clock_running = False
        state.clock_seconds = 180.0
    elif opcode == opcodes.OP_CLOCK_SET:
        state.clock_seconds = float(payload)
    else:
        log.warning("Unknown opcode 0x%02X (payload=%s)", opcode, payload)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Fencing Scoreboard")
    parser.add_argument("--port",   default=config.DEFAULT_PORT, help="Serial port (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud",   default=config.DEFAULT_BAUD, type=int, help="Baud rate")
    parser.add_argument("--demo",   action="store_true", help="Demo/simulate mode — no serial required")
    parser.add_argument("--width",  default=config.SCREEN_WIDTH,  type=int)
    parser.add_argument("--height", default=config.SCREEN_HEIGHT, type=int)
    parser.add_argument("--windowed", action="store_true", help="Run in a window instead of fullscreen")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # --- Pygame init ---
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=config.MIXER_BUFFER)

    flags = 0 if args.windowed else pygame.FULLSCREEN
    screen = pygame.display.set_mode((args.width, args.height), flags)
    pygame.display.set_caption("Fencing Scoreboard")
    pygame.mouse.set_visible(False)

    display.load_fonts()

    # --- Audio ---
    audio_mgr = audio.AudioManager()

    # --- State ---
    state = BoutState()
    cmd_queue: queue.Queue = queue.Queue()

    # --- Serial (skipped in demo mode) ---
    if not args.demo:
        start_serial_reader(args.port, args.baud, cmd_queue)
        log.info("Serial reader started on %s @ %d", args.port, args.baud)
    else:
        log.info("Demo mode active — use keyboard keys to inject events (see README)")

    clock = pygame.time.Clock()
    last_ticks = pygame.time.get_ticks()

    dirty = True           # force an initial render on startup
    was_window_active = False
    detector = DisconnectDetector()

    # --- Main loop ---
    running = True
    while running:
        now_ms = pygame.time.get_ticks()
        dt_s   = (now_ms - last_ticks) / 1000.0
        last_ticks = now_ms

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif args.demo and event.key in DEMO_KEYS:
                    op, pl = DEMO_KEYS[event.key]
                    cmd_queue.put((op, pl))

        # Drain the command queue (serial thread or demo injections)
        while True:
            try:
                opcode, payload = cmd_queue.get_nowait()
            except queue.Empty:
                break
            apply_command(opcode, payload, state, audio_mgr, detector, now_ms)
            dirty = True

        # Tick the clock — only dirty when the displayed MM:SS value changes
        if state.clock_running and state.clock_seconds > 0:
            prev_int = int(state.clock_seconds)
            state.clock_seconds = max(0.0, state.clock_seconds - dt_s)
            if state.clock_seconds == 0.0:
                state.clock_running = False
            if int(state.clock_seconds) != prev_int:
                dirty = True

        # Update disconnect detector (checks silence period, clears mute if elapsed)
        detector.update(now_ms)

        # Detect hit window expiry — need one more render when indicators go dark
        is_window_active = _window_active(state, now_ms)
        if was_window_active and not is_window_active:
            dirty = True
        was_window_active = is_window_active

        # Clear delta display after timeout
        if (state.delta_ms is not None and state.delta_set_time is not None and
                (now_ms - state.delta_set_time) >= config.DELTA_DISPLAY_MS):
            state.delta_ms       = None
            state.delta_set_time = None
            dirty = True

        # Auto-reset scores after winner fanfare delay
        if state.winner_reset_at is not None and now_ms >= state.winner_reset_at:
            state.reset_scores()
            state.reset_indicators()
            dirty = True

        # Render only when something visible has changed
        if dirty:
            display.render(screen, state, now_ms)
            pygame.display.flip()
            dirty = False

        clock.tick(config.FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
