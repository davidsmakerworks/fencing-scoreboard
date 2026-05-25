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
| `bout_win_score` | 5 | Score that triggers the winner announcement and auto-reset |
| `winner_reset_delay_ms` | 5000 | Minimum delay after the winner announcement before scores are reset to zero (ms); actual reset waits until the announcement finishes if longer |

### `timing`
| Key | Default | Description |
|-----|---------|-------------|
| `hit_indicator_duration_ms` | 2500 | How long hit indicators stay lit after a hit signal (ms) |
| `hit_window_ms` | 300 | Reference window for the double-hit pie-chart visualisation — a full wedge represents this duration (ms) |
| `delta_display_ms` | 10000 | How long the Δt reading stays on screen before auto-clearing (ms) |
| `disconnect_hit_count` | 3 | Number of hit signals within `disconnect_window_ms` that triggers buzzer mute |
| `disconnect_window_ms` | 12500 | Rolling window for disconnect detection (ms) |
| `disconnect_silence_ms` | 5000 | Silence period required to restore the buzzer after a disconnect (ms) |

### `audio`
| Key | Description |
|-----|-------------|
| `hit_on_target_file` | WAV played immediately on an on-target hit |
| `hit_off_target_file` | WAV played immediately on an off-target (white) hit |
| `reset_file` | WAV played on score reset |
| `touch_left_file` | Touch call played at the start of a point or winner announcement for the left (red) fencer |
| `touch_right_file` | Touch call played at the start of a point or winner announcement for the right (green) fencer |
| `mixer_buffer` | SDL audio buffer size in samples (increase if audio crackles; 2048 recommended for Pi) |
| `tones.hit_on_target` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.hit_off_target` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.reset` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.touch` | Fallback sequence `{notes}` when touch WAV is absent — each note is `{frequency, duration_ms}` |

#### `audio.announcement` — speech-cadence gaps
| Key | Default | Description |
|-----|---------|-------------|
| `gap_after_touch_ms` | 750 | Pause after the touch call before "the score is" / "the winner is" |
| `gap_between_words_ms` | 200 | Pause between individual phrase words (e.g., between "the score is" and the first number) |
| `gap_between_scores_ms` | 200 | Pause between the two score numbers when scores differ |
| `gap_score_to_all_ms` | 100 | Shorter pause before "all" when scores are tied |
| `gap_after_winner_name_ms` | 400 | Pause after the fencer name before "the final score is" |

### `layout`, `fonts`, `colors`
Fractional screen-position values, font sizes, and RGB color tuples.
All layout values are fractions of the screen dimensions so the display
scales automatically when `width`/`height` change.

| Layout key | Description |
|------------|-------------|
| `indicator_outline_width` | Stroke width in pixels used to draw indicator bars in their off (unlit) state |

---

## Audio

### Immediate sounds
These files play instantly on the corresponding event:

| File | Played when |
|------|-------------|
| `sounds/hit_on_target.wav`  | On-target hit (left, right, or both) |
| `sounds/hit_off_target.wav` | Off-target (white) hit |
| `sounds/reset.wav`          | Score reset |

### Announcement sounds
These files are sequenced automatically by the announcement system.
All files should be mono WAV, 44100 Hz, 16-bit.

**Touch calls** (played at the start of every point/winner announcement):

| File | Used when |
|------|-----------|
| `sounds/touch_left.wav`  | Left (red) fencer scores or wins |
| `sounds/touch_right.wav` | Right (green) fencer scores or wins |

**Phrase files** (fixed words strung together per announcement):

| File | Content |
|------|---------|
| `sounds/the_score_is.wav`       | "The score is" |
| `sounds/the_final_score_is.wav` | "The final score is" |
| `sounds/the_winner_is.wav`      | "The winner is" |
| `sounds/the_fencer_to_my_left.wav`  | "The fencer to my left" |
| `sounds/the_fencer_to_my_right.wav` | "The fencer to my right" |
| `sounds/all.wav`                | "All" (used for tied scores, e.g., "three all") |

**Number files** (one per score value, 0–15):

| Files |
|-------|
| `sounds/zero.wav` … `sounds/fifteen.wav` |

If a touch WAV file is missing, a synthesised two-tone sequence is used as a fallback
(configurable under `audio.tones.touch` in `config.json`).
If any phrase or number WAV file is missing, that item is silently skipped in the
announcement sequence.

---

## Scoring and bout winner

### Point announcement
When a fencer scores a point below the winning score, the following sequence plays:

1. Touch call (`touch_left.wav` or `touch_right.wav`)
2. Pause (`gap_after_touch_ms`)
3. "The score is" (`the_score_is.wav`)
4. Brief pause (`gap_between_words_ms`)
5. Score of the fencer who scored (called first, regardless of which is higher)
6. Either: pause + other fencer's score (`gap_between_scores_ms`) — or — shorter pause + "all" (`gap_score_to_all_ms`) if tied

### Winner announcement
When a fencer's score reaches `bout_win_score` (default 5):

1. Touch call (`touch_left.wav` or `touch_right.wav`)
2. Pause (`gap_after_touch_ms`)
3. "The winner is" (`the_winner_is.wav`)
4. Brief pause (`gap_between_words_ms`)
5. Fencer name (`the_fencer_to_my_left.wav` or `the_fencer_to_my_right.wav`)
6. Pause (`gap_after_winner_name_ms`)
7. "The final score is" (`the_final_score_is.wav`)
8. Brief pause (`gap_between_words_ms`)
9. Winner's score, then loser's score (same cadence as point announcement)

After the full announcement finishes (plus a 1-second buffer), both scores are
automatically reset to zero and all indicators are cleared.
A manual `SCORE_RESET` opcode cancels any pending auto-reset immediately.

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

## Double-hit delta display

When the hardware sends a `DELTA_TIME` opcode, the centre of the screen shows:

- The numeric Δt value in milliseconds
- A pie-chart wedge whose filled arc represents the delta as a fraction of
  `hit_window_ms` (a full circle = at or beyond the reference window)
- A filled arrow below the pie chart indicating which fencer's hit was received
  first:
  - **Bright red, pointing left** — the left (red) fencer hit first
  - **Bright green, pointing right** — the right (green) fencer hit first
  - No arrow — both hits were simultaneous (`HIT_BOTH` opcode)

The display clears automatically after `delta_display_ms` (default 10 seconds).
A new `DELTA_TIME` opcode before that time replaces the display and resets the
timer.

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
- When **lit**, indicator bars are drawn solid. When **off**, they are drawn as
  an outline only (stroke width set by `indicator_outline_width` in `config.json`).

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
audio.py         — sound loading, tone generation, and announcement scheduling
config.json      — all tuneable configuration
sounds/          — WAV files (synthesised tones used as fallback if absent)
requirements.txt
```
