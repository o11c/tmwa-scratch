#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    create.py - parse arguments to determine files to create from templates
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

# Requires Python 2.6 or later.
from __future__ import print_function, division

# Global imports
import sys
import os

if sys.version_info[0] != 2:
    print("Unsupported major version - please use python 2.6 or 2.7")
    print("(Are you ignoring my shebang on purpose?)")
    os.getenv('I_WANT_TO_BREAK_STUFF') or sys.exit(1)
    print("Continue at your own risk!")

try:
    import argparse
except ImportError:
    print("This program requires the 'argparse' module")
    print("See http://pypi.python.org/pypi/argparse")
    sys.exit(1)


# Local imports
import templates

_stats = set()
# TODO: cover all the corner cases where path appears to exist.
# hardlink: done
# is symlink
# broken symlink: exists() is False; creates the target
def open_create(name):
    # print('open_create:', name)
    stat = None
    if os.path.exists(name):
        stat = os.stat(name)
        if stat.st_size:
            raise argparse.ArgumentError('file already exists and is not empty: %r' % name)
    ret = open(name, 'w')
    if stat is None:
        stat = os.stat(name)
    if stat in _stats:
        raise argparse.ArgumentError("wtf? opened same file multiple times! (evil sym/hard links?)")
    _stats.add(stat)
    return ret


class NamedFile(object):
    """ A pair of open (for writing) file and apparent name.

    """
    def __init__(self, f, n):
        self.file = f
        self.name = n

class FakeContainer(object):
    def __init__(self):
        self.named_files = []
        self.have_stdout = False
        self.used_files = set()

    files = property()
    @files.setter
    def files(self, real_names):
        #if real_names is None:
        #    return
        # print('add files:', real_names)
        for real_name in real_names:
            if real_name in self.used_files:
                raise argparse.ArgumentError('file %r specified more than once' % real_name)
            self.used_files.add(real_name)
            self.named_files.append(NamedFile(open_create(real_name), real_name))

    to_stdout = property()
    @to_stdout.setter
    def to_stdout(self, fake_name):
        #if fake_name is None:
        #    return
        if self.have_stdout:
            raise argparse.ArgumentError('--to-stdout must be specified at most once!')
        self.have_stdout = True
        if fake_name in self.used_files:
            raise argparse.ArgumentError('file %r specified more than once' % real_name)
        self.used_files.add(fake_name)
        # print('add stdout:', fake_name)
        self.named_files.append(NamedFile(sys.stdout, fake_name))

    to = property()
    @to.setter
    def to(self, real_and_fake):
        #if real_and_fake is None:
        #    return
        real_name, fake_name = real_and_fake
        if real_name in self.used_files:
            raise argparse.ArgumentError('file %r specified more than once' % real_name)
        self.used_files.add(real_name)
        if fake_name in self.used_files:
            raise argparse.ArgumentError('file %r specified more than once' % real_name)
        self.used_files.add(fake_name)
        print('fake:', real_name, 'to:', fake_name)
        self.named_files.append(NamedFile(open_create(real_name), fake_name))


parser = argparse.ArgumentParser(
        description="Create files from templates",
        fromfile_prefix_chars='@',
        argument_default=argparse.SUPPRESS,
)
parser.add_argument(
        'files', #dest
        nargs='*',
        help='files to create directly',
)
parser.add_argument(
        '--to',
        nargs=2,
        help='a file to "create" in a different file',
        metavar=('file', 'name'),
)
parser.add_argument(
        '--to-stdout',
#        nargs=1,
        help='a file to "create" to stdout',
        metavar='name',
)

opts = parser.parse_args(namespace=FakeContainer())

# print('opts.named_files:', opts.named_files)

if not opts.named_files:
    parser.print_help()
    sys.exit(1)

for nf in opts.named_files:
    templates.parse(nf)
