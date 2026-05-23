# Fencing Scoreboard

Fullscreen kiosk-style fencing scoreboard built with Python + Pygame.  
Runs on Windows and Linux (Raspberry Pi).

---

## Requirements

```
pip install -r requirements.txt
```

Python 3.10+ recommended.

---

## How to run

### Fullscreen (normal operation)
```bash
python main.py --port COM3 --baud 115200
```

On Linux/Raspberry Pi:
```bash
python main.py --port /dev/ttyUSB0 --baud 115200
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

## Configuring the serial port

Pass `--port` and `--baud` on the command line, or edit the defaults in `config.py`:

```python
DEFAULT_PORT = "COM3"       # Windows; use /dev/ttyUSB0 on Linux
DEFAULT_BAUD = 115200
```

---

## Audio

Place WAV files in the `sounds/` directory:

| File | Purpose |
|------|---------|
| `sounds/hit_on_target.wav`  | Played on every on-target hit |
| `sounds/hit_off_target.wav` | Reserved for future off-target sound |
| `sounds/reset.wav`          | Played on score reset |

If a file is missing, a synthesised tone is generated automatically (requires `numpy`).

---

## Serial protocol

Commands are single-byte opcodes.  Two opcodes carry a 2-byte big-endian `uint16` payload immediately after the opcode byte:

| Opcode | Hex | Payload | Description |
|--------|-----|---------|-------------|
| SCORE_LEFT_INC  | 0x01 | — | Left score +1 |
| SCORE_LEFT_DEC  | 0x02 | — | Left score −1 |
| SCORE_RIGHT_INC | 0x03 | — | Right score +1 |
| SCORE_RIGHT_DEC | 0x04 | — | Right score −1 |
| SCORE_RESET     | 0x05 | — | Reset both scores + indicators |
| HIT_LEFT        | 0x10 | — | On-target hit, left fencer |
| HIT_RIGHT       | 0x11 | — | On-target hit, right fencer |
| HIT_BOTH        | 0x12 | — | Simultaneous hit |
| WHITE_LEFT      | 0x20 | — | Off-target left (visual only) |
| WHITE_RIGHT     | 0x21 | — | Off-target right (visual only) |
| DELTA_TIME      | 0x30 | uint16 ms | Double-hit time delta |
| CLOCK_START     | 0x40 | — | Start countdown |
| CLOCK_STOP      | 0x41 | — | Stop countdown |
| CLOCK_RESET     | 0x42 | — | Reset to 3:00, stopped |
| CLOCK_SET       | 0x43 | uint16 s | Set clock to given seconds |

---

## Adding new opcodes

1. Add a constant in `config.py` (`OP_MY_NEW_CMD = 0xXX`).
2. If it carries a payload, add it to `UINT16_PAYLOAD_OPS` in `config.py`.
3. Add a handler branch in `apply_command()` in `main.py`.
4. Add a demo key binding in `DEMO_KEYS` in `main.py` if useful.
5. Add a display element in `display.py` if needed.

---

## Project structure

```
main.py          — entry point, main loop, state mutation
serial_reader.py — daemon thread, opcode parser
display.py       — all rendering (stateless, driven by BoutState)
state.py         — BoutState dataclass
config.py        — constants, colors, opcode table
audio.py         — sound loading + playback
sounds/          — WAV files (auto-generated tones if absent)
requirements.txt
```
