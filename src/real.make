#!/usr/bin/env make -rRf

##    real.make - The One Makefile that builds them all.
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

ifeq (${MAKE_RESTARTS},)
ifeq ($(findstring s,$(firstword ${MAKEFLAGS})),)
# Note: the space is necessary
# TODO: look for an elvish unicode subset?
$(info )
$(info Welcome to the One Makefile)
$(info Copyright 2012 Ben Longbons)
$(info )
$(info One Makefile to build them all,)
$(info One Makefile to find them,)
$(info One Makefile to bring them all)
$(info and in the darkness link them.)
$(info )
endif
else
$(info Restarting due to regenerated makefiles.)
endif

ifeq ($(findstring r, $(firstword ${MAKEFLAGS})),)
$(error Please specify -r)
endif
ifeq ($(findstring R, $(firstword ${MAKEFLAGS})),)
$(error Please specify -R)
endif
ifneq "${MAKEFILE_LIST}" " src/real.make"
$(error not used as sole toplevel makefile!)
endif

# variables like CXX, LDFLAGS
include build.conf
# variables like prefix, pkgdatadir
include install.conf

# dummy rules for now
default: ; echo Hi
src/real.make: FORCE; touch $@
FORCE:
