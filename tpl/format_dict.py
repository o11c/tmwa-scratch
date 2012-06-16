#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    format_dict.py - expand keywords in templates, with callables
##
##    Copyright © 2012 Ben Longbons <b.r.longbons@gmail.com>
##
##    This file is part of The Mana World (Athena server)
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Global imports
from __future__ import print_function, division

import string

_formatter = string.Formatter()

class _Proxy(object):
    """ Call callables with a __format__

        string.Formatter.vformat handles ':' specially,
        and calls format() with the rhs, after expanding it.

        So we override __format__.

        Note that '{foo}' and '{foo:}' are identical - fmt is ''.
    """
    def __init__(self, val):
        self.value = val
    def __format__(self, fmt):
        # print('Call __format__: %r with %r' % (self.value, fmt))
        if (callable(self.value)):
            if not fmt:
                ret = self.value()
            else:
                ret = self.value(fmt)
            if ret is None:
                # print("Return: None (omitted)")
                return ''
            # print("Return: %r" % ret)
            return str(ret)
        else:
            # print("Format: %r with %r" % (self.value, fmt))
            # Somebody might actually use this like it's meant to be used
            return format(self.value, fmt)

class FormatDict(dict):
    """ A dictionary-like object that can be used with a template.

        If a key in the string contains a ':', whatever is before that
        must be a unary callable function, and the right side is passed,
        after first being recursively expanded.

        Otherwise, return like an ordinary dictionary,
        except that a nullary callable gets dethunked.
    """
    def format(self, template):
        # .vformat calls with a depth of 2! That's insane and useless!
        # the set() argument is unused in the implementation
        return _formatter._vformat(template, (), self, set(), 0xFFFFFFFF)

    def __getitem__(self, key):
        return _Proxy(dict.__getitem__(self, key))
