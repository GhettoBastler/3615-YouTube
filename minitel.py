#!/usr/bin/env python

import encoding
from serial import (
    Serial,
    SEVENBITS,
    PARITY_EVEN
)

ESC = b'\x1b'
CSI = ESC + b'\x5b'
PRO1 = ESC + b'\x39'
PRO2 = ESC + b'\x3A'
PRO3 = ESC + b'\x3B'
PROG = b'\x6b'
CURSOR_ON = b'\x11'
CURSOR_OFF = b'\x14'
CLEAR_SCREEN = b'\x0c'
RESET_MINITEL = b'\x7f'

BAUDRATES = {
    300: 2,
    1200: 4,
    4800: 6,
}


class InvalidBaudrateError(Exception):

    def __init__(self, br):
        msg = f'Baudrate cannot be set to {br}. Valid values are 300, 1200 and 4800.'
        super().__init__(msg)


class Minitel:

    def __init__(self, port='/dev/ttyAMA0', baudrate=1200):
        self.conn = Serial(port, baudrate, SEVENBITS, PARITY_EVEN)

    def cursor_on(self, status=True):
        if status:
            self.conn.write(b'\x11')
        else:
            self.conn.write(b'\x14')

    def echo_on(self, status=True):
        """
        Turns local echo ON or OFF"""
        if status:
            command = b'\x61'
        else:
            command = b'\x60'
        msg = PRO3 + command + b'\x5a' + b'\x51'
        self.conn.write(msg)

    def set_baudrate(self, baudrate):
        if baudrate not in BAUDRATES:
            raise InvalidBaudrateError(baudrate)

        # Building 'set baudrate' message
        br = BAUDRATES[baudrate]
        br_byte = (1 << 6) | (br << 3) | br

        msg = PRO2 + PROG + bytes((br_byte,))

        self.conn.write(msg)
        self.conn.flush()
        self.conn.baudrate = baudrate

    def write_bytes(self, b):
        self.conn.write(b)
        self.conn.flush()

    def write_text(self, text):
        b = encoding.encode(text)
        self.write_bytes(b)
        self.conn.flush()

    def read_until_send(self):
        res = self.conn.read_until(b'\x13A')
        return res[:-2]

    def move_cursor(self, pos):
        x_val = 64 + pos[0]
        y_val = 64 + pos[1]
        msg = b'\x1f' + bytes((y_val, x_val))
        self.write_bytes(msg)

    def read_key(self):
        self.conn.read_all()  # Flush input
        key = self.conn.read(1)

        if key in encoding.DECODING_TABLE:  # Printable character
            return encoding.decode(key).encode('utf-8')
        elif key == b'\x19':  # Special or accent
            key += self.conn.read(1)
            if key in encoding.DECODING_TABLE:  # Special
                return encode.decode(key).encode('utf-8')
            elif key[-1] in b'\x41\x42\x43\x48\x4b':  # Accent
                key += self.conn.read(1)
                if key in encoding.DECODING_TABLE:  # Found accentuated character
                    return encoding.decode(key).encode('utf-8')
                else:  # Invalid accent
                    if key[-1] in encoding.DECODING_TABLE:  # Outputing unaccentuated character
                        return encoding.decode(key[-1]).encode('utf-8')
                    else:  # Invalid code, aborting
                        return None
            else:  # Invalid code, aborting
                return None
        elif key == b'\x13':  # Function key
            key += self.conn.read(1)
            return key
        elif key == ESC:  # Escape key
            return key
        else:  # Unknown code, aborting
            return None

    def input(self, max_len, buff=b'', placeholder=b'.'):
        end_bs = [b'\x13Y', b'\r', b'\x13A', b'\x13B']
        end = False

        # Filing field with placeholders
        fill_len = max_len - len(buff)
        self.cursor_on(False)
        self.write_bytes(fill_len * placeholder)
        self.write_bytes(b'\x08' * fill_len)

        self.cursor_on(True)
        while not end:
            b = self.read_key()
            if not b:
                continue
            if b in end_bs:
                break
            elif b.startswith(b'\x13'):  # Function key
                if b == b'\x13G':  # Correction key
                    if buff:
                        buff = buff[:-1]
                        self.write_bytes(b'\x08' + placeholder + b'\x08')  # Replace last character with a placeholder
                elif b == b'\x13E':  # Cancel key
                    self.write_bytes(b'\x08' * len(buff) + placeholder * max_len + b'\x08' * max_len)
                    buff = b''
            else:
                if len(buff) < max_len:
                    buff += b
                    self.write_bytes(encoding.transcode(b))
        return (buff, b)

    def clear_screen(self):
        self.conn.write(CLEAR_SCREEN)

    def __close__(self):
        self.conn.close()
