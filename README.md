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

The following keys work in **all modes** (demo and normal):

| Key   | Action |
|-------|--------|
| S     | Start / stop clock (toggle) |
| N     | Full reset — scores, indicators, and clock |
| Space | Start sequence (en garde → ready → fence → clock starts) |
| L     | Cycle score limit (5 → 10 → 15 → 5) |
| ESC   | Quit |

In demo mode, these additional keys inject hardware events:

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
| G   | Clock reset (3:00) |
| V   | Set clock to 3:00 |

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
| `bout_win_score` | 5 | Starting score limit; the value that triggers the winner announcement and auto-reset. Can be changed at runtime (see [Score limit](#score-limit)). |
| `winner_reset_delay_ms` | 5000 | Minimum delay after the winner announcement before scores are reset to zero (ms); actual reset waits until the announcement finishes if longer |

### `gamepad`
| Key | Default | Description |
|-----|---------|-------------|
| `score_limit_button` | 1 | Button ID that cycles the score limit |
| `reset_button` | 2 | Button ID for full reset (scores, indicators, and clock) |
| `clock_toggle_button` | 3 | Button ID that starts/stops the clock (or cancels a pending start sequence) |
| `start_sequence_button` | 0 | Button ID that launches the en-garde / ready / fence start sequence |

Button numbering starts at 0. Consult your controller's documentation or use a gamepad test utility to identify button indices.

### `start_sequence`
| Key | Default | Description |
|-----|---------|-------------|
| `initial_delay_ms` | 2000 | Pause between button press and the "en garde" call (ms) |
| `random_delay_min_ms` | 750 | Minimum random pause between calls (ms) |
| `random_delay_max_ms` | 2000 | Maximum random pause between calls (ms) |

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
| `halt_file` | WAV played (or queued) when the countdown clock reaches zero |
| `time_expired_file` | Phrase WAV played after the halt sound at time expiry (skipped if absent) |
| `en_garde_file` | First call in the start sequence (skipped if absent) |
| `ready_file` | Second call in the start sequence (skipped if absent) |
| `fence_file` | Third call in the start sequence; clock starts when it finishes (skipped if absent) |
| `tones.hit_on_target` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.hit_off_target` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.reset` | Fallback tone `{frequency, duration_ms}` when WAV is absent |
| `tones.touch` | Fallback sequence `{notes}` when touch WAV is absent — each note is `{frequency, duration_ms}` |
| `tones.halt_beeps` | Fallback for `halt_file` — `{notes, repeats}` generating a rapid beep sequence |

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
When a fencer's score reaches the current score limit (default 5; changeable at runtime — see [Score limit](#score-limit)):

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
automatically reset to zero, all indicators are cleared, and the clock is reset
to 3:00 (stopped).
A manual `SCORE_RESET` opcode cancels any pending auto-reset immediately.

---

## Score limit

The score limit (the score that ends a bout and triggers the winner announcement)
can be changed at runtime without restarting the application. It cycles through
**5 → 10 → 15 → 5** and is never written back to `config.json` — the change
applies only for the current session.

| Input | Action |
|-------|--------|
| Keyboard **L** | Cycle score limit (works in all modes) |
| Gamepad button `gamepad_score_limit_button` (default **1**) | Cycle score limit |

Each time the limit changes, a status message — e.g. **Score limit: 10** —
appears centred at the bottom of the screen for 2 seconds.

To change the default button ID, set `gamepad_score_limit_button` in `config.json`
under `game`. Button numbering starts at 0; consult your controller's documentation
or test with a gamepad utility to find the right button index.

---

## Game controller

Any gamepad or joystick recognised by SDL (via Pygame) can be connected before or
after the application starts — hot-plug is supported. When a controller is detected,
a log message identifies it by name and instance ID.

The following actions are mapped to controller buttons (all configurable under
`gamepad` in `config.json`):

| Button (default) | Action |
|-----------------|--------|
| 0 | Start sequence (en garde → ready → fence → clock starts) |
| 1 | Cycle score limit |
| 2 | Full reset — scores, indicators, and clock |
| 3 | Start / stop clock (or cancel a pending start sequence) |

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

## Start sequence

Pressing the start-sequence button (default: gamepad button 4, or **Space** on keyboard)
launches the pre-bout announcement sequence:

1. **Pause** — `initial_delay_ms` (default 2 s) after the button press.
2. **"En garde"** — `sounds/en_garde.wav` plays (silently skipped if absent).
3. **Random pause** — between `random_delay_min_ms` and `random_delay_max_ms` (default 750 – 2000 ms).
4. **"Ready"** — `sounds/ready.wav` plays (silently skipped if absent).
5. **Random pause** — same range as above.
6. **"Fence"** — `sounds/fence.wav` plays (silently skipped if absent).
7. **Clock starts** as soon as "fence" finishes.

All three timings are configurable under `start_sequence` in `config.json`.

Pressing **S** (or the clock-toggle button) while the sequence is pending cancels it
without starting the clock. Pressing the start-sequence button again while one is
already running cancels the previous sequence and begins a fresh one.
The clock is stopped when the sequence begins, so an accidental double-press is safe.

---

## Clock display

The clock is rendered as **M:SS** (single digit for minutes, two digits for
seconds — e.g. `3:00`, `0:45`). No leading zero is shown for minutes.

The colon changes colour to indicate clock state:

| State | Colon colour |
|-------|-------------|
| Running | Yellow |
| Stopped | Same grey as the digit colour |

---

## Clock behaviour during a bout

### Stopping on a hit

Any hit signal (on-target or off-target, from either fencer) stops the clock
immediately if it is running. Only the *first* hit of an exchange triggers the
stop; subsequent hits within the same display window have no additional effect
on the clock because it is already stopped.

### Time expiry

When the countdown clock reaches zero the following sequence occurs automatically:

1. **Halt** — `sounds/halt.wav` plays if the file exists; otherwise a rapid series
   of 6 synthesised beeps is used as a fallback (configurable under
   `audio.tones.halt_beeps` in `config.json`).
2. **Time expired** — `sounds/time_expired.wav` plays if the file exists
   (silently skipped otherwise).
3. **Announcement** — the winner and final score are announced (no touch call):
   - If one fencer leads: "The winner is … the final score is …"
   - If the scores are tied: "The score is X all"
   - The winner is determined by the higher score regardless of the configured
     score limit.
4. Scores **auto-reset** and the clock resets to 3:00 after the announcement
   finishes (same delay as a normal winner announcement: `winner_reset_delay_ms`).

While the clock is at zero — from the moment it expires until a clock reset
(`G` key in demo mode, or `CLOCK_RESET` / `CLOCK_SET` serial opcodes) — **all
hit signals are ignored**. This prevents spurious scoring after time runs out.

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
