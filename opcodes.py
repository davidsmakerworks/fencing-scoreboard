# opcodes.py — serial protocol constants shared with the scoring hardware firmware.
# These are semi-permanent; changing them requires a matching firmware update.

FRAME_START = 0xAA  # preamble byte that precedes every packet on the TTL link

OP_SCORE_LEFT_INC  = 0x01
OP_SCORE_LEFT_DEC  = 0x02
OP_SCORE_RIGHT_INC = 0x03
OP_SCORE_RIGHT_DEC = 0x04
OP_SCORE_RESET     = 0x05

OP_HIT_LEFT        = 0x10  # on-target left  — triggers sound + visual
OP_HIT_RIGHT       = 0x11  # on-target right — triggers sound + visual
OP_HIT_BOTH        = 0x12  # simultaneous hit

OP_WHITE_LEFT      = 0x20  # off-target left  (visual + sound)
OP_WHITE_RIGHT     = 0x21  # off-target right (visual + sound)

OP_DELTA_TIME      = 0x30  # uint16 payload: milliseconds between hits

OP_CLOCK_START     = 0x40
OP_CLOCK_STOP      = 0x41
OP_CLOCK_RESET     = 0x42
OP_CLOCK_SET       = 0x43  # uint16 payload: seconds

# Opcodes that carry a big-endian uint16 payload immediately after the opcode byte
UINT16_PAYLOAD_OPS = {OP_DELTA_TIME, OP_CLOCK_SET}

# Human-readable names (used for logging and demo mode)
OPCODE_NAMES = {
    OP_SCORE_LEFT_INC:  "SCORE_LEFT_INC",
    OP_SCORE_LEFT_DEC:  "SCORE_LEFT_DEC",
    OP_SCORE_RIGHT_INC: "SCORE_RIGHT_INC",
    OP_SCORE_RIGHT_DEC: "SCORE_RIGHT_DEC",
    OP_SCORE_RESET:     "SCORE_RESET",
    OP_HIT_LEFT:        "HIT_LEFT",
    OP_HIT_RIGHT:       "HIT_RIGHT",
    OP_HIT_BOTH:        "HIT_BOTH",
    OP_WHITE_LEFT:      "WHITE_LEFT",
    OP_WHITE_RIGHT:     "WHITE_RIGHT",
    OP_DELTA_TIME:      "DELTA_TIME",
    OP_CLOCK_START:     "CLOCK_START",
    OP_CLOCK_STOP:      "CLOCK_STOP",
    OP_CLOCK_RESET:     "CLOCK_RESET",
    OP_CLOCK_SET:       "CLOCK_SET",
}
