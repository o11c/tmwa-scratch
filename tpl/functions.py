#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    functions.py - useful things to expand in a template
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

# This file exists to keep the imports clean in the other files

from __future__ import print_function, division

import datetime
import subprocess
import re

def add_to(d):
    d.update(
        year = lambda: datetime.date.today().year,
        # These work because of __str__
        date = datetime.date.today,
        datetime = datetime.datetime.now,

        include = lambda filename: open(filename).read(),

        # These are normally called as methods, but this works just as well.
        upper = str.upper,
        lower = str.lower,

        # Turn argument into a valid C identifier
        identifier = identifier,
        initials = initials,

        eval = eval,
        repr = repr,
        # TODO: close stdin
        shell = lambda cmd: subprocess.check_output(arg, shell=True),

        # Useful with {include}
        reparse = lambda name: (
            d.format(name)
        ),

        # Regexen!
        replace = regex_replace,
        prepend = prepend,
    )

def identifier(name):
    return ('_' * name[0].isdigit() +
        "".join(
                [c if c.isalnum() else '_' for c in name]
        ).strip('_')
    )

def initials(words):
    return filter(str.isupper, words)

def regex_replace(args):
    pattern, replacement, body = args.strip('\n').split('\n', 2)
    # Body may have other \n
    return re.sub(pattern, replacement, body)

def prepend(args):
    prefix, body = args.strip('\n').split('\n', 1)
    # Which of these is more Pythonic?
    return prefix + body.replace('\n', '\n' + prefix)
    return '\n'.join(map(lambda w: prefix + w, s.split('\n')))
