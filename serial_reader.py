# serial_reader.py — daemon thread that reads bytes from serial and pushes
# parsed (opcode, optional_payload) tuples into a queue.Queue.

import threading
import queue
import struct
import logging
from typing import Optional

import serial

import config
import opcodes

log = logging.getLogger(__name__)


def _read_exactly(port: serial.Serial, n: int) -> Optional[bytes]:
    """Read exactly n bytes; return None if the port closes mid-read."""
    buf = b""
    while len(buf) < n:
        chunk = port.read(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _reader_loop(port_name: str, baud: int, cmd_queue: queue.Queue, stop_event: threading.Event):
    """Main body of the serial daemon thread."""
    try:
        with serial.Serial(port_name, baud, timeout=0.1) as port:
            log.info("Serial port %s opened at %d baud", port_name, baud)
            while not stop_event.is_set():
                # Seek to the next FRAME_START byte, discarding anything before it.
                # This resyncs cleanly after noise, a firmware reset, or a mid-stream connect.
                raw = port.read(1)
                if not raw:
                    continue
                if raw[0] != opcodes.FRAME_START:
                    log.debug("Discarding out-of-frame byte: 0x%02X", raw[0])
                    continue

                raw = port.read(1)
                if not raw:
                    continue
                opcode = raw[0]
                payload = None

                if opcode in opcodes.UINT16_PAYLOAD_OPS:
                    data = _read_exactly(port, 2)
                    if data is None:
                        log.warning("Serial port closed while reading payload")
                        break
                    (payload,) = struct.unpack(">H", data)  # big-endian uint16

                cmd_queue.put((opcode, payload))
    except serial.SerialException as exc:
        log.error("Serial error: %s", exc)


def start_serial_reader(port_name: str, baud: int, cmd_queue: queue.Queue) -> threading.Event:
    """
    Spawn a daemon thread that reads from *port_name* and pushes commands into
    *cmd_queue*.  Returns a stop_event that the caller can set to request shutdown.
    """
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_reader_loop,
        args=(port_name, baud, cmd_queue, stop_event),
        daemon=True,
        name="serial-reader",
    )
    thread.start()
    return stop_event
