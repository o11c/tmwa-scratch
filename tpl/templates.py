#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    templates.py - generate new files from templates
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

from __future__ import print_function, division

# Global imports
import sys
import os

# Local imports
import config
import format_dict
import functions

fdict = format_dict.FormatDict()
config.load_into(fdict)
functions.add_to(fdict)

def parse(nf):
    file = nf.file
    name = nf.name

    # If name is a/b/c/d.e
    # path = a/b/c
    # filename = d.e
    # module = c
    # root = d
    # ext = e
    path, filename = os.path.split(name)
    module = os.path.basename(path)
    root, ext = os.path.splitext(filename)
    if not ext:
        raise Exception('File %r has no extension' % name)
    # Skip the .
    ext = ext[1:]

    fdict.update(
        module = module,
        filename = filename,
        root = root,
        ext = ext,
        # TODO: maybe read this interactively or something?
        description = "<TODO: describe this file briefly>",
    )
    template = open(config.template_for_ext(ext)).read()
#    contents = template.format(**fdict)
    contents = fdict.format(template)

    file.write(contents)
    file.close()
