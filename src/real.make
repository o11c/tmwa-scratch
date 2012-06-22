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
# TODO: should I write this in tengwar?
# The major problem is that it's usually encoded in the PUA
# and thus requires a font specification.
# There *is* a formal request and tentative allocation in the SMP,
# but it has been languishing for 15 years.
# TODO: regardless of the preceding, look up the words for 'build' and 'link'.
# (Does there exist a word that could mean "makefile"?
# Maybe something like 'instructional scroll')

# Note: the space is necessary
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
$(info Restarting (${MAKE_RESTARTS}) due to regenerated makefiles.)
endif

# Somebody should file a bug against the Make documentation
# - in the example, it doesn't mention that firstword is needed
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

###############################################################################

## Preferred usage: don't call this directly, use the configure script!

# This is the real makefile, called with -f from the build dir.
# Important note: the build dir is not the current directory.
# Note also that it is called with -r -R, so we have no clutter

SHELL := /bin/bash

ifneq (debug,)
override debug = $(info $1: $(value $1))
endif

SOURCES := $(shell find src/ -name '*.cpp')
$(call debug,SOURCES)
INCLUDES := $(wildcard include/tmwa/*.hpp)
$(call debug,INCLUDES)

# Note: 'sort' removes duplicates
SUBDIRS := $(patsubst src/%/,%,$(sort $(dir ${SOURCES})))
$(call debug,SUBDIRS)

OBJS := $(patsubst src/%.cpp,%.o,${SOURCES})
$(call debug,OBJS)
ASMS := $(patsubst src/%.cpp,%.s,${SOURCES})
$(call debug,ASMS)
CPPS := $(patsubst src/%.cpp,%.ii,${SOURCES})
$(call debug,CPPS)
DEPS := $(patsubst src/%.cpp,%.d,${SOURCES})
$(call debug,DEPS)
MAINS := $(filter src/%/main.cpp,${SOURCES})
$(call debug,MAINS)
TESTS := $(filter src/%/test.cpp,${SOURCES})
$(call debug,TESTS)
ILIBS := $(filter src/%/lib.cpp,${SOURCES})
$(call debug,ILIBS)

BINS := $(patsubst src/%/main.cpp,bin/%,${MAINS})
$(call debug,BINS)
BINTESTS := $(patsubst src/%/test.cpp,bin/%-test,${TESTS})
$(call debug,BINTESTS)
ARS := $(patsubst src/%/lib.cpp,lib/%.a,${ILIBS})
$(call debug,ARS)

# Building .so.1.0.0 files is not supported because it's not easy.
# (might be slightly easier with clang and -emit-llvm ?)

# For test targets
WRAPPER :=
# WRAPPER := gdb --args
ARGS :=

.DEFAULT_GOAL = default

MKDIRS = @mkdir -p ${@D}
AR = ar

# this is needed, because % needs to match a path/basename in the following
vpath %.cpp src

%.d : %.cpp
	$(MKDIRS)
# Note: the -MT specifies that the .o, .d, .s, and .ii all depend on the stuff
# NOTE: the first sed removes backslash-newline and compresses extra spaces
# NOTE: the second sed is to remove dir/../ (dir must not be a symlink)
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -MM $< -MP -MT '$@ $(patsubst %.d,%.o,$@) $(patsubst %.d,%.s,$@) $(patsubst %.d,%.ii,$@)' -o - \
		| sed -e 'H;/\\$$/d;z;x;s/\\\n/ /g' -e 's/\s\+/ /g;s/^ //;s/ $$//;/^$$/d' \
		| sed -e ':loop;s:[^/. ]\+/\.\./::g;t loop' \
		> $@
%.o : %.cpp
	$(MKDIRS)
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -c $< -o $@
# Not actually needed for the build, but allows me to check whether my code appeases the compiler.
%.s : %.cpp
	$(MKDIRS)
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -S $< -o $@ -fverbose-asm -masm=intel
%.ii : %.cpp
	$(MKDIRS)
	${CXX} ${CXXFLAGS} ${CPPFLAGS} -E $< -o $@

# No need for deps or a separate bin/%-test rule
bin/% :
	$(MKDIRS)
	${CXX} ${LDFLAGS} $^ ${LIBS} -o $@
	# Do I want this like this? TODO look at the embedding mode again
	ln -sf ../src/main-gdb-py $@-gdb.py

# NOTE: 'ar' puts files in archives excluding paths.
# However, it will insert and use duplicates just fine.
# So, there is no problem with same-named files in different directories.
lib/%.a :
	$(MKDIRS)
	rm -f $@ # to destroy old .o files
	ar rc $@ $^
# Force remaking before the fancy stuff happens
include ${DEPS}

define RECURSIVE_DEPS_IMPL
$(eval more_deps := $(shell cat ${1}))
$(eval more_deps := $(patsubst src/%.hpp,%.d,${more_deps}))
$(eval more_deps := $(patsubst include/tmwa/%.hpp,%/lib.d,${more_deps}))
$(eval more_deps := $(filter ${DEPS},${more_deps}))
$(eval more_deps := $(filter-out ${cur_deps},${more_deps}))
$(eval cur_deps += ${more_deps})
$(foreach dep,${more_deps},$(call RECURSIVE_DEPS_IMPL,${dep}))
endef

define RECURSIVE_DEPS
$(eval cur_deps := ${1})
$(call RECURSIVE_DEPS_IMPL,${1})

$(patsubst %.d,%.${intermediate},${cur_deps})
endef

# The $(eval) is needed to fix lineishness
$(foreach exe,${BINS},$(eval ${exe} : $(strip $(call RECURSIVE_DEPS,$(patsubst bin/%,%/main.d,${exe})))))
$(foreach exe,${BINTESTS},$(eval ${exe} : $(strip $(call RECURSIVE_DEPS,$(patsubst bin/%-test,%/test.d,${exe})))))
$(foreach lib,${ARS},$(eval ${lib} : $(strip $(call RECURSIVE_DEPS,$(patsubst lib/%.a,%/lib.d,${lib})))))

$(foreach dir,${SUBDIRS},                                       		\
    $(eval ${dir}/objects:      $(filter ${dir}/%,${OBJS}))     		\
    $(eval ${dir}/asms:      	$(filter ${dir}/%,${ASMS}))				\
    $(eval ${dir}/mains:        $(filter bin/${dir},${BINS}))   		\
    $(eval ${dir}/tests:        $(filter bin/${dir}-test,${BINTESTS})) 	\
    $(eval ${dir}/libs:         $(filter lib/${dir}.a,${ARS})) 			\
)
# Note: without the ; this deletes rules instead of declaring
%/bins: %/mains %/tests ;
# Also add %/libs here
%/default: %/bins %/libs ;
%/all: %/objects %/default ;

#No commands, just forward for convenience when calling from the subdir
%/main : bin/% ;
# Same, but also run it
%/test : bin/%-test
	${WRAPPER} $< ${ARGS}
%/lib : lib/%.a ;

.PHONY: none all default objects install clean
none:
objects: $(addsuffix /objects,${SUBDIRS})
asms: $(addsuffix /asms,${SUBDIRS})
mains: $(addsuffix /mains,${SUBDIRS})
tests: $(addsuffix /tests,${SUBDIRS})
libs: $(addsuffix /libs,${SUBDIRS})
bins: $(addsuffix /bins,${SUBDIRS})
default: $(addsuffix /default,${SUBDIRS})
all: $(addsuffix /all,${SUBDIRS})

install: # No deps - install whatever managed to get built
#Note: need to make sure $(wildcard ${FOO}) is not empty

# What about the ones I should put in libexec?
	install -t ${bindir} $(wildcard ${BINS})
#	install -t ${includedir} $(wildcard ${INCLUDES})
#	install -t ${libdir} $(wildcard ${ARS})
#	install -t ${pkgdatadir} <everything in data/>
#	install -t ${sysconfdir} <everything in etc/>
clean:
	rm -rf ${SUBDIRS} bin lib

help:
	less src/make.help
