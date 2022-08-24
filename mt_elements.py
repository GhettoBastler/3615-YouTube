#!/usr/bin/env python

import encoding


class UpdatableText:

    def _filled(self):
        n = self.length - len(self.value[:self.length])
        return self.value + n * ' '

    def __init__(self, mt, pos, length, value=''):
        self.mt = mt
        self.pos = pos
        self.length = length
        self.value = value

    def update(self, value=''):
        self.value = value
        self.mt.cursor_on(False)
        self.mt.move_cursor(self.pos)
        self.mt.write_text(self._filled())


class ProgressBar:

    def __init__(self, mt, pos, length, p=0):
        self.mt = mt
        self.pos = pos
        self.length = length
        self.p = p

    def update(self, p=0):
        self.p = p
        fill_len = int(self.p * self.length)
        empty_len = self.length - fill_len
        bs = b'\x0e' + b'\x5f' * fill_len + b'\x0f' + b'_' * empty_len

        self.mt.cursor_on(False)
        self.mt.move_cursor(self.pos)
        self.mt.write_bytes(bs)
