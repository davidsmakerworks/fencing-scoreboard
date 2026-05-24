# Fencing Scoreboard

Fullscreen kiosk-style fencing scoreboard built with Python + Pygame.
Runs on Windows and Linux (Raspberry Pi).

---

## Requirements

```
pip install -r requirements.txt
```

Python 3.10+ required.

---

## How to run

### Fullscreen (normal operation)
```bash
python main.py
```

The serial port and baud rate default to the values in `config.json`.
Override on the command line if needed:

```bash
python main.py --port /dev/ttyUSB0 --baud 19200
```

### Windowed (for development)
```bash
python main.py --demo --windowed --width 1280 --height 720
```

### Demo / simulate mode
Run without any serial hardware attached:
```bash
python main.py --demo
```

In demo mode, use the keyboard to inject events:

| Key | Action |
|-----|--------|
| Q   | Left score +1 |
| A   | Left score −1 |
| E   | Right score +1 |
| D   | Right score −1 |
| R   | Reset scores + indicators |
| Z   | On-target hit — left |
| X   | On-target hit — right |
| C   | Simultaneous hit (both) |
| 1   | Off-target (white) — left |
| 2   | Off-target (white) — right |
| 3   | Delta-time example (83 ms) |
| S   | Clock start |
| T   | Clock stop |
| G   | Clock reset (3:00) |
| V   | Set clock to 3:00 |
| ESC | Quit |

---

## Configuration

All tuneable values live in `config.json`. The file is read at startup;
no recompilation is needed to change settings.

### `screen`
| Key | Description |
|-----|-------------|
| `width`, `height` | Resolution in pixels |
| `fps` | Maximum frame rate (acts as a polling cap; frames are only rendered when the display changes) |

### `serial`
| Key | Description |
|-----|-------------|
| `default_port` | Serial port used when `--port` is not passed (`COM3` on Windows, `/dev/ttyUSB0` on Linux) |
| `default_baud` | Baud rate |

### `game`
| Key | Default | Description |
|-----|---------|-------------|
| `bout_win_score` | 5 | Score that triggers the winner fanfare and auto-reset |
| `winner_reset_delay_ms` | 5000 | Delay after the winner fanfare before scores are reset to zero (ms) |

### `timing`
| Key | Default | Description |
|-----|---------|-------------|
| `hit_indicator_duration_ms` | 2500 | How long hit indicators stay lit after a hit signal (ms) |
| `hit_window_ms` | 300 | Reference window for the double-hit pie-chart visualisation (ms) |
| `delta_display_ms` | 10000 | How long the Δt reading stays on screen before auto-clearing (ms) |
| `disconnect_hit_count` | 3 | Number of hit signals within `disconnect_window_ms` that triggers buzzer mute |
| `disconnect_window_ms` | 12500 | Rolling window for disconnect detection (ms) |
| `disconnect_silence_ms` | 5000 | Silence period required to restore the buzzer after a disconnect (ms) |

### `audio`
| Key | Description |
|-----|-------------|
| `hit_on_target_file` | WAV played on an on-target hit |
| `hit_off_target_file` | WAV played on an off-target (white) hit |
| `reset_file` | WAV played on score reset |
| `winner_left_file` | WAV played when the left (red) fencer wins the bout |
| `winner_right_file` | WAV played when the right (green) fencer wins the bout |
| `point_left_file` | WAV played when the left fencer scores a point |
| `point_right_file` | WAV played when the right fencer scores a point |
| `mixer_buffer` | SDL audio buffer size in samples (increase if audio crackles; 2048 recommended for Pi) |
| `tones.hit_on_target` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.hit_off_target` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.reset` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.winner` | Fallback sequence `{notes, repeats}` when WAV is absent — each note is `{frequency, duration_ms}`; `frequency: 0` is silence |
| `tones.point` | Fallback sequence `{notes}` when WAV is absent |

### `layout`, `fonts`, `colors`
Fractional screen-position values, font sizes, and RGB color tuples.
All layout values are fractions of the screen dimensions so the display
scales automatically when `width`/`height` change.

---

## Audio

Place WAV files in the `sounds/` directory:

| File | Played when |
|------|-------------|
| `sounds/hit_on_target.wav`  | On-target hit (left, right, or both) |
| `sounds/hit_off_target.wav` | Off-target (white) hit |
| `sounds/reset.wav`          | Score reset |
| `sounds/winner_left.wav`    | Left (red) fencer reaches the winning score |
| `sounds/winner_right.wav`   | Right (green) fencer reaches the winning score |
| `sounds/point_left.wav`     | Left fencer scores a point (below the winning score) |
| `sounds/point_right.wav`    | Right fencer scores a point (below the winning score) |

If a WAV file is missing, a synthesised fallback is generated automatically
using `numpy`. Simple tones use `{frequency, duration_ms}`; the winner fanfare
uses a configurable multi-note sequence with optional silence and a repeat
count — all defined under `audio.tones` in `config.json`.

---

## Serial protocol

The hardware module communicates over a raw TTL serial link.
Every packet begins with the framing byte `0xAA`, followed by a single
opcode byte. Two opcodes carry an additional 2-byte big-endian `uint16`
payload immediately after the opcode.

```
[ 0xAA ] [ opcode ] [ payload_hi ] [ payload_lo ]   ← uint16 opcodes only
[ 0xAA ] [ opcode ]                                  ← all other opcodes
```

The `0xAA` preamble lets the receiver resync after noise or a firmware
reset without manual intervention.

| Opcode | Hex | Payload | Description |
|--------|-----|---------|-------------|
| SCORE_LEFT_INC  | 0x01 | —          | Left score +1 |
| SCORE_LEFT_DEC  | 0x02 | —          | Left score −1 |
| SCORE_RIGHT_INC | 0x03 | —          | Right score +1 |
| SCORE_RIGHT_DEC | 0x04 | —          | Right score −1 |
| SCORE_RESET     | 0x05 | —          | Reset both scores and all indicators |
| HIT_LEFT        | 0x10 | —          | On-target hit, left fencer |
| HIT_RIGHT       | 0x11 | —          | On-target hit, right fencer |
| HIT_BOTH        | 0x12 | —          | Simultaneous on-target hit |
| WHITE_LEFT      | 0x20 | —          | Off-target (white) hit, left fencer |
| WHITE_RIGHT     | 0x21 | —          | Off-target (white) hit, right fencer |
| DELTA_TIME      | 0x30 | uint16 ms  | Double-hit time delta |
| CLOCK_START     | 0x40 | —          | Start countdown clock |
| CLOCK_STOP      | 0x41 | —          | Stop countdown clock |
| CLOCK_RESET     | 0x42 | —          | Reset clock to 3:00, stopped |
| CLOCK_SET       | 0x43 | uint16 s   | Set clock to given seconds |

Opcode constants are defined in [`opcodes.py`](opcodes.py).

---

## Disconnect detection

Continuous hit signals caused by a disconnected foil will mute the
buzzer automatically. When `disconnect_hit_count` (default 3) hit signals
are received within `disconnect_window_ms` (default 12 500 ms), the buzzer
is silenced. Visual indicators continue to operate normally throughout.

The buzzer is restored once no hit signal has been received for
`disconnect_silence_ms` (default 5 000 ms). All three values are
configurable in `config.json` under `timing`.

---

## Hit indicator behaviour

- The **first** hit signal in an exchange lights the appropriate indicator(s)
  and plays the buzzer.
- Any further hit signals received while the indicators are still lit update
  the visuals silently — the buzzer does not re-trigger.
- Both the on-target (red/green) and off-target (yellow) indicator bars share
  a single display window and extinguish simultaneously when it expires.
- For each side, only one of on-target or off-target can be active at a time
  (enforced by the hardware module).

---

## Scoring and bout winner

- When a fencer scores a point below the winning score, the corresponding
  `point_left.wav` or `point_right.wav` is played.
- When a fencer's score reaches `bout_win_score` (default 5), the winner
  fanfare (`winner_left.wav` / `winner_right.wav`) plays instead.
- After `winner_reset_delay_ms` (default 5 000 ms) both scores are
  automatically reset to zero and all indicators are cleared.
- A manual `SCORE_RESET` opcode cancels any pending auto-reset immediately.

---

## Adding new opcodes

1. Add a constant in [`opcodes.py`](opcodes.py): `OP_MY_NEW_CMD = 0xXX`
2. If it carries a uint16 payload, add it to `UINT16_PAYLOAD_OPS` in the same file.
3. Add a handler branch in `apply_command()` in [`main.py`](main.py).
4. Add a demo key binding in `DEMO_KEYS` in [`main.py`](main.py) if useful for testing.
5. Add a display element in [`display.py`](display.py) if needed.

---

## Project structure

```
main.py          — entry point, arg parsing, main loop, state mutation,
                   disconnect detection
serial_reader.py — daemon thread, framing + opcode parser
display.py       — all rendering (driven by BoutState; only redraws on change)
state.py         — BoutState dataclass (single source of truth)
config.py        — loads config.json and exposes values as module-level names
opcodes.py       — serial protocol constants (firmware-matched hex values)
audio.py         — sound loading and playback helpers
config.json      — all tuneable configuration
sounds/          — WAV files (synthesised tones used as fallback if absent)
requirements.txt
```
