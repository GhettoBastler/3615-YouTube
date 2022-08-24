#!/usr/bin/env python

from string import (
    ascii_letters,
    digits,
)


class UnsupportedCharacterError(Exception):
    def __init__(self, c):
        msg = f'Character {c} can not be displayed on the Minitel'
        super().__init__(msg)


class UnknownByteStringError(Exception):
    def __init__(self, bs):
        msg = f'Byte string {bs} does not translate to any known character'
        super().__init__(msg)


SS2 = b'\x19'
ACCENT_GRAVE = b'\x41'
ACCENT_AIGU = b'\x42'
ACCENT_CIRCONFLEXE = b'\x43'
TREMA = b'\x48'
CEDILLE = b'\x4b'

LETTERS = {c: bytes((ord(c),)) for c in ascii_letters}
DIGITS = {d: bytes((ord(d),)) for d in digits}

PUNCTUATION = {
    '!': b'\x21',
    '"': b'\x22',
    '#': b'\x23',
    '$': b'\x24',
    '%': b'\x25',
    '&': b'\x26',
    '\'': b'\x27',
    '(': b'\x28',
    ')': b'\x29',
    '*': b'\x2a',
    '+': b'\x2b',
    ',': b'\x2c',
    '-': b'\x2d',
    '.': b'\x2e',
    '/': b'\x2f',
    ':': b'\x3a',
    ';': b'\x3b',
    '<': b'\x3c',
    '=': b'\x3d',
    '>': b'\x3e',
    '?': b'\x3f',
    '@': b'\x40',
    '[': b'\x5b',
    '\\': b'\x5c',
    ']': b'\x5d',
    '_': b'\x5f',
    '|': b'\x7c',
    ' ': b'\x20',
}

ACCENTUATED = {
    'à': SS2 + ACCENT_GRAVE + b'a',
    'è': SS2 + ACCENT_GRAVE + b'e',
    'ù': SS2 + ACCENT_GRAVE + b'u',
    'é': SS2 + ACCENT_AIGU + b'e',
    'â': SS2 + ACCENT_CIRCONFLEXE + b'a',
    'ê': SS2 + ACCENT_CIRCONFLEXE + b'e',
    'î': SS2 + ACCENT_CIRCONFLEXE + b'i',
    'ô': SS2 + ACCENT_CIRCONFLEXE + b'o',
    'û': SS2 + ACCENT_CIRCONFLEXE + b'u',
    'ä': SS2 + TREMA + b'a',
    'ë': SS2 + TREMA + b'e',
    'ï': SS2 + TREMA + b'i',
    'ö': SS2 + TREMA + b'o',
    'ü': SS2 + TREMA + b'u',
    'ç': SS2 + CEDILLE + b'c',
}

SPECIAL = {
    'œ': SS2 + b'\x7a',
    'Œ': SS2 + b'\x6a',
    'ß': SS2 + b'\x7b',
    '£': SS2 + b'\x23',
    '§': SS2 + b'\x27',
    '←': SS2 + b'\x2c',
    '↑': SS2 + b'\x2d',
    '→': SS2 + b'\x2e',
    '↓': SS2 + b'\x2f',
    '°': SS2 + b'\x30',
    '±': SS2 + b'\x31',
    '÷': SS2 + b'\x38',
    '¼': SS2 + b'\x3c',
    '½': SS2 + b'\x3d',
    '¾': SS2 + b'\x3e',
}

CONTROL = {
    '\r': b'\x0d',
    '\t': b'\x09',
    '\n': b'\x0a',
}

PRINTABLE = LETTERS | ACCENTUATED | DIGITS | PUNCTUATION | SPECIAL
ENCODING_TABLE = PRINTABLE | CONTROL
DECODING_TABLE = {v: k for k, v in ENCODING_TABLE.items()}


def clean(text, repl='_'):
    '''
    Replaces all non-encodable characters with a placeholder'''
    res = ''
    for c in text:
        if c not in ENCODING_TABLE:
            res += repl
        else:
            res += c
    return res


def encode(text):
    res = b''
    for c in text:
        if c in ENCODING_TABLE:
            res += ENCODING_TABLE[c]
        else:
            raise UnsupportedCharacterError(c)
    return res


def decode(bs):
    res = ''
    while bs:
        if bs[:3] in DECODING_TABLE:
            key = bs[:3]
            bs = bs[3:]
        elif bs[:2] in DECODING_TABLE:
            key = bs[:2]
            bs = bs[2:]
        elif bs[:1] in DECODING_TABLE:
            key = bs[:1]
            bs = bs[1:]
        else:
            raise UnknownByteStringError(bs[:3])
        res += DECODING_TABLE[key]
    return res


def transcode(bs):
    txt = bs.decode('utf-8')
    return encode(txt)
