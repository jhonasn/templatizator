'''Helpers for interface'''
import re

_NONBMP = re.compile(r'[\U00010000-\U0010FFFF]')


def _surrogatepair(match):
    char = match.group()
    assert ord(char) > 0xffff
    encoded = char.encode('utf-16-le')
    return (
        chr(int.from_bytes(encoded[:2], 'little')) +
        chr(int.from_bytes(encoded[2:], 'little')))


def get_tkinter_unicode(text):
    '''Convert unicode icon to unicode pair that is readable to tkinter'''
    return _NONBMP.sub(_surrogatepair, text.upper())
