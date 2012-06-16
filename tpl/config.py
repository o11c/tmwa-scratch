#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    config.py - load variables from a config file
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

import os
import sys

_self_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

def load_into(d):
    d['conf_dir'] = _self_dir
    path = os.path.join(_self_dir, 'conf')
    if not os.path.exists(path):
        print("%r does not exist, please create it from %r" % (path, path + '.example'))
        sys.exit(1)
    execfile(path, {}, d)

def template_for_ext(ext):
    return os.path.join(_self_dir, 'template.' + ext)
