#!/usr/bin/env python
# -*- encoding: utf-8 -*-

##    configure.py - A minimal configure script that's not retarded.
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

import sys
import os
import subprocess
from collections import OrderedDict

# If you're porting this configure script for another project,
# here's a list of things you probably need to change:
# * The entries in all_features, all_packages, and all_options.
# * The hard-coded expansion logic from those, and the try_compile clauses.
# * The package name right here.
package_name = 'The Mana World (Athena server)'
package = 'tmwa'

def die(msg, *args):
    sys.exit('Fatal: ' + msg % args)

def symlink(target, name):
    if os.path.exists(name):
        if os.readlink(name) == target:
            pass
        else:
            die('Symlink %r exists but is not pointing to %r', name, target)
    else:
        os.symlink(target, name)
# function symlink

def tablify(list_of_lists):
    lengths = []
    for lst in list_of_lists:
        for i in xrange(len(lst)):
            if i == len(lengths):
                lengths.append(len(lst[i]))
            else:
                lengths[i] = max(lengths[i], len(lst[i]))
            # if
        # for i
    # for lst
    for lst in list_of_lists:
        line = []
        for i in xrange(len(lst)):
            line.append(lst[i].ljust(lengths[i]))
        yield ' '.join(line)
    # for lst
# function tablify

def parse_bool(s):
    if s == 'yes':
        return True
    if s == 'no':
        return False
    die('%r is not a boolean', s)
# function parse_bool

# These values are assumed in various places,
# but here so their length can be used for slicing
OPT_ENABLE = '--enable-'
OPT_DISABLE = '--disable-'
OPT_WITH = '--with-'
OPT_WITHOUT = '--without-'
OPT_USE = '--use-'
OPT_NO = '--no-'

class Main(object):
    __slots__ = ('general', 'dirs', 'features', 'packages', 'options', 'vars',
        '_compiler_and_flags', '_sloppy')

    aliases = OrderedDict([
        ('--dev', ['--clang', '--enable-warnings']),
        ('--clang', ['CXX=clang++']),
        ('--home', ['--prefix='+(os.getenv('HOME') or die("$HOME not set!"))]),
    ])

    all_general = OrderedDict([
        ('build',       'Prefix used for native toolchain [none]'),
        ('host',        'Prefix used for actual toolchain [BUILD]'),
        ('prefix',      'architecture-independent files [/usr/local]'),
        ('exec-prefix', 'architecture-dependent files [PREFIX]'),
    ])
    # these are all the directories I've seen with a typical configure script
    # not all of them are used by me, or by anyone (/usr/local/com ???)
    all_dirs = OrderedDict([
        ('bin',         'user executables [EPREFIX/bin]'),
        ('sbin',        'system admin executables [EPREFIX/sbin]'),
        ('libexec',     'program executables [EPREFIX/libexec]'),
        ('sysconf',     'read-only single-machine data [PREFIX/etc]'),
        ('sharedstate', 'modifiable architecture-independent data [PREFIX/com]'),
        ('localstate',  'modifiable single-machine data [PREFIX/var]'),
        ('lib',         'object code libraries [EPREFIX/lib]'),
        ('include',     'C header files [PREFIX/include]'),
        ('oldinclude',  'C header files for non-gcc [/usr/include]'),
        ('dataroot',    'read-only arch.-independent data root [PREFIX/share]'),
        ('data',        'read-only architecture-independent data [DATAROOTDIR]'),
        # I added this one because it's useful
        ('pkgdata',     'read-only data files for this package [DATADIR/%s]' % package),
        ('info',        'info documentation [DATAROOTDIR/info]'),
        ('locale',      'locale-dependent data [DATAROOTDIR/locale]'),
        ('man',         'man documentation [DATAROOTDIR/man]'),
        ('doc',         'documentation root [DATAROOTDIR/doc/%s]' % package),
        ('html',        'html documentation [DOCDIR]'),
        ('dvi',         'dvi documentation [DOCDIR]'),
        ('pdf',         'pdf documentation [DOCDIR]'),
        ('ps',          'ps documentation [DOCDIR]'),
    ])
    # --enable- / --disable
    all_features = OrderedDict([
        ('option-checking', 'Be strict about unknown options. [yes]'),
        ('warnings',        'Warnings useful during development'),
        # nls seems like a --with to me, but everyone else puts it here.
        ('nls',             'Enable translation where available. [no]'),
    ])
    # --with- / --without-
    all_packages = OrderedDict([
        ('boost',   "Specify the the directory containing <boost/> headers."),
    ])
    # --use-
    all_options = OrderedDict([
        ('lto',         "Enable link-time optimization."),
        ('assembly',    "Generate .s files instead of .o files.")
    ])

    all_vars = OrderedDict([
        ('LDFLAGS',     'linker flags; e.g. -L /usr/lib/foo/'),
        ('LIBS',        'libraries to pass to the linker; e.g. -lfoo'),
        ('CPPFLAGS',    'preprocessor flags; e.g. -I /usr/include/foo/'),
        ('CXX',         'C++ compiler command. [g++ or BUILD-g++]'),
        ('CXXFLAGS',    'C++ compiler flags. [-g -O2]'),
    ])


    def help(self):
        print('Usage: <path>/configure [--option[=value]]... [VAR=value]...')
        print('  --disable-FOO means --enable-FOO=no, likewise --without-FOO.')
        print("  An omitted argument is interpreted as 'yes'.")
        print('General options:')
        for line in tablify(
            [
                ['    --'+key+'=', value]
                    for key, value in Main.all_general.iteritems()
            ]
        ):
            print(line)
        # for line
        print('Fine-tuned install directories:')
        for line in tablify(
            [
                ['    --'+key+'dir=', value]
                    for key, value in Main.all_dirs.iteritems()
            ]
        ):
            print(line)
        # for line
        print('Optional features:')
        for line in tablify(
            [
                ['    --enable-'+key+'=', value]
                    for key, value in Main.all_features.iteritems()
            ]
        ):
            print(line)
        # for line
        print('External packages:')
        for line in tablify(
            [
                ['    --with-'+key+'=', value]
                    for key, value in Main.all_packages.iteritems()
            ]
        ):
            print(line)
        # for line
        print('Build options:')
        for line in tablify(
            [
                ['    --use-'+key+'=', value]
                    for key, value in Main.all_options.iteritems()
            ]
        ):
            print(line)
        # for line
        print('Variables:')
        for line in tablify(
            [
                ['    '+key+'=', value]
                    for key, value in Main.all_vars.iteritems()
            ]
        ):
            print(line)
        # for line
        print('And finally, some shortcuts:')
        for line in tablify(
            [
                ['    '+key, ' '.join(value)]
                    for key, value in Main.aliases.iteritems()
            ]
        ):
            print(line)
        # for line
    # method help

    def die(self, msg, *args):
        if self._sloppy:
            sys.stderr.write(msg % args)
            sys.stderr.write('\n')
        else:
            die(msg, *args)

    def parse(self, arg):
        expansion = Main.aliases.get(arg, None)
        if expansion is not None:
            for word in expansion:
                self.parse(word)
            return
        if not arg.startswith('-'):
            # variable
            if '=' not in arg:
                die('non-option argument %r has no assignment!', arg)
            var, val = arg.split('=', 1)
            var in Main.all_vars or self.die('Unknown variable %r', var)
            self.vars[var] = val
            return
        if not arg.startswith('--'):
            die('Argument %r is a a short option, not supported', arg)

        # TODO: efficientize this (it's not *that* bad)
        if arg.startswith(OPT_NO):
            if '=' in arg:
                die("value not allowed in %r", arg)
            arg = '--' + arg[len(OPT_NO):] + '=no'
        if arg.startswith(OPT_DISABLE):
            if '=' in arg:
                die("value not allowed in %r", arg)
            arg = OPT_ENABLE + arg[len(OPT_DISABLE):] + '=no'
        if arg.startswith(OPT_WITHOUT):
            if '=' in arg:
                die("value not allowed in %r", arg)
            arg = OPT_WITH + arg[len(OPT_WITHOUT):] + '=no'

        if '=' not in arg:
            arg += '=yes'
        opt, val = arg.split('=', 1)

        if opt.startswith(OPT_ENABLE):
            key = opt[len(OPT_ENABLE):]
            if key == 'option-checking':
                self._sloppy = not parse_bool(val)
            key in Main.all_features or self.die('Unknown feature %r', key)
            self.features[key] = val
        elif opt.startswith(OPT_WITH):
            key = opt[len(OPT_WITH):]
            key in Main.all_packages or self.die('Unknown package %r', key)
            self.packages[key] = val
        elif opt.startswith(OPT_USE):
            key = opt[len(OPT_USE):]
            key in Main.all_options or self.die('Unknown build option %r', key)
            self.options[key] = val
        elif opt.endswith('dir'):
            key = opt[2:-3]
            key in Main.all_dirs or self.die('Unknown install dir %r', key)
            self.dirs[key] = val
        else:
            key = opt[2:]
            key in Main.all_general or self.die('Unknown argument %r', key)
            self.general[key] = val
    # method parse

    def __init__(self, argv):
        if '--help' in argv:
            self.help()
            sys.exit(0)

        root, base = os.path.split(argv[0])

        if base != 'configure':
            die('Identity crisis!')

        if root == '.':
            print("Redirecting './' to 'build/'.")
            os.path.isdir('build') or os.mkdir('build')
            with open('GNUmakefile', 'w') as mf:
                mf.write('.DEFAULT_GOAL = default\n')
                mf.write('%:: ; ${MAKE} -C build $@\n')
            os.chdir('build')
            root = '..'

        print("Assuming the build environment is sane.")
        self.general = {}
        self.dirs = {}
        self.features = {}
        self.packages = {}
        self.options = {}
        self.vars = {}
        self._sloppy = False

        symlink(os.path.join(root, 'src'), 'src')
        symlink(os.path.join(root, 'include'), 'include')

        # first, record all the variables
        for arg in argv[1:]:
            self.parse(arg)

        ## First build/host and then vars, because they are essential

        # Note: the use of 'or' instead of the default argument to dict.get()
        # is intentional for two reasons:
        # 1. It treats empty string as undefined, granting a global 'reset'
        # 2. it defers the calculation of the default if it is not used.

        # toolset to use to build intermediary programs
        build = self.general.get('build') or 'native'
        # toolset to use to build actual programs
        # (yes, this use of 'host' is confusing)
        host = self.general.get('host') or build

        # These lines will be written to build.conf
        build_conf = []

        # note: these will be exported to the makefile
        # and may be overridden by passing arguments to 'make'
        # however, other options will be forced
        CXX = self.vars.get('CXX') or (
            'g++' if host == 'native'
            else host + '-g++'
        )
        build_conf.append('CXX := '+CXX)
        CPPFLAGS = self.vars.get('CPPFLAGS') or ''
        build_conf.append('CPPFLAGS := '+CPPFLAGS)
        CXXFLAGS = self.vars.get('CXXFLAGS') or '-g -O2 -pipe'
        build_conf.append('CXXFLAGS := '+CXXFLAGS)
        LDFLAGS = self.vars.get('LDFLAGS') or ''
        build_conf.append('LDFLAGS := '+LDFLAGS)
        LIBS = self.vars.get('LIBS') or ''
        build_conf.append('LIBS := '+LIBS)

        # for use with the try_compile function
        # lets hope that *FLAGS don't contain a "
        self._compiler_and_flags = [CXX] + CPPFLAGS.split() + CXXFLAGS.split()

        for cxx11_flag in ['-std=c++11', '-std=c++0x']:
            if self.try_compile(
                '''
constexpr bool get_true() { return true; }
static_assert(get_true(), "This message cannot happen.");
''',
                extra_flags=[cxx11_flag]
            ):
                build_conf.append('override CXXFLAGS += '+cxx11_flag)
                self._compiler_and_flags.append(cxx11_flag)
                break
        else:
            die('Unable to locate a sufficient C++11 compiler!')


        ## Next external packages, because they are likely to fail.

        boost = self.packages.get('boost')
        if boost in ['yes', 'no']:
            die('--with-boost= is not a boolean option!')
        if boost:
            self._compiler_and_flags.append('-I')
            self._compiler_and_flags.append(boost)
            build_conf.append('override CPPFLAGS += -I ' + boost)
        self.try_compile('#include <boost/multi_index_container_fwd.hpp>') or die('boost not found!')

        ## Next optional features, because they also might fail.
        # (note, option-checking is handled specially)
        nls = self.features.get('nls')
        if nls:
            if parse_bool(nls):
                pass
            print("Note, feature 'nls' isn't actually implemented yet.")
        # if nls
        warnings = self.features.get('warnings')
        if warnings and parse_bool(warnings):
            build_conf.append('override CPPFLAGS += -include tmwa/warnings.hpp')
        # if warnings

        ## Then almost-finally build-options
        lto = self.options.get('lto')
        if lto and parse_bool(lto):
            build_conf.append('override CXXFLAGS += -flto')
            build_conf.append('override LDFLAGS += -flto')
        # if lto

        assembly = self.options.get('assembly')
        if assembly:
            if parse_bool(assembly):
                pass
            print("Note, option 'assembly' isn't actually implemented yet.")
        # if assembly


        ## Now finally (for real), the install dirs
        # These lines will be written to install.conf
        install_conf = []

        prefix =            self.dirs.get('prefix') or '/usr/local'
        eprefix =           self.dirs.get('exec-prefix') or prefix

        bindir =            self.dirs.get('bin') or eprefix + '/bin'
        sbindir =           self.dirs.get('sbin') or eprefix + '/sbin'
        libexecdir =        self.dirs.get('libexec') or eprefix + '/libexec'
        sysconfdir =        self.dirs.get('sysconf') or prefix + '/etc'
        sharedstatedir =    self.dirs.get('sharedstate') or prefix + '/com'
        localstatedir =     self.dirs.get('localstate') or prefix + '/var'
        libdir =            self.dirs.get('lib') or prefix + '/lib'
        includedir =        self.dirs.get('include') or prefix + '/include'
        oldincludedir =     self.dirs.get('oldinclude') or '/usr/include'
        datarootdir =       self.dirs.get('dataroot') or prefix + '/share'
        datadir =           self.dirs.get('data') or datarootdir
        pkgdatadir =        self.dirs.get('pkgdata') or datadir + '/' + package
        infodir =           self.dirs.get('info') or datarootdir + '/info'
        localedir =         self.dirs.get('locale') or datarootdir + '/locale'
        mandir =            self.dirs.get('man') or datarootdir + '/man'
        docdir =            self.dirs.get('doc') or datarootdir + '/doc/' + package
        htmldir =           self.dirs.get('html') or docdir
        dvidir =            self.dirs.get('dvi') or docdir
        pdfdir =            self.dirs.get('pdf') or docdir
        psdir =             self.dirs.get('ps') or docdir

        # DESTDIR is specified at install time and has no trailing slash.
        install_conf.append('prefix := ${DESTDIR}' + prefix)
        install_conf.append('exec-prefix := ${DESTDIR}' + eprefix)
        install_conf.append('bindir := ${DESTDIR}' + bindir)
        install_conf.append('sbindir := ${DESTDIR}' + sbindir)
        install_conf.append('libexecdir := ${DESTDIR}' + libexecdir)
        install_conf.append('sysconfdir := ${DESTDIR}' + sysconfdir)
        install_conf.append('sharedstatedir := ${DESTDIR}' + sharedstatedir)
        install_conf.append('localstatedir := ${DESTDIR}' + localstatedir)
        install_conf.append('libdir := ${DESTDIR}' + libdir)
        install_conf.append('includedir := ${DESTDIR}' + includedir)
        install_conf.append('oldincludedir := ${DESTDIR}' + oldincludedir)
        install_conf.append('datarootdir := ${DESTDIR}' + datarootdir)
        install_conf.append('datadir := ${DESTDIR}' + datadir)
        install_conf.append('pkgdatadir := ${DESTDIR}' + pkgdatadir)
        install_conf.append('infodir := ${DESTDIR}' + infodir)
        install_conf.append('localedir := ${DESTDIR}' + localedir)
        install_conf.append('mandir := ${DESTDIR}' + mandir)
        install_conf.append('docdir := ${DESTDIR}' + docdir)
        install_conf.append('htmldir := ${DESTDIR}' + htmldir)
        install_conf.append('dvidir := ${DESTDIR}' + dvidir)
        install_conf.append('pdfdir := ${DESTDIR}' + pdfdir)
        install_conf.append('psdir := ${DESTDIR}' + psdir)


        # Only write the actual makefiles if nothing went wrong
        with open('build.conf', 'w') as bc:
            for line in build_conf:
                bc.write(line)
                bc.write('\n')

        with open('install.conf', 'w') as ic:
            for line in install_conf:
                ic.write(line)
                ic.write('\n')

        with open('Makefile', 'w') as mf:
            mf.write('.DEFAULT_GOAL = default\n')
            mf.write('%:: FORCE; ${MAKE} -rRf src/real.make $@\n')
            mf.write('FORCE: ;\n')
            mf.write('Makefile: ;\n')

        with open('config.status', 'w') as status:
            status.write(
"""#!/usr/bin/env python
from __future__ import print_function, division
import sys
import os
if len(sys.argv) != 1:
    print('This script takes no arguments')
    print('It just calls configure again with remembered arguments')
else:
    os.execv(%r, %r)
# TODO: handle being in a different directory
""" % (argv[0], argv)
            )
        os.chmod('config.status', os.stat('config.status').st_mode | 0111)

        print('Everything is Ok.')
    # method __init__

    def try_compile(self, prog, extra_flags=[]):
        process = subprocess.Popen(
            self._compiler_and_flags + extra_flags + ['-x', 'c++', '-', '-fsyntax-only'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None
        ) # stdout discarded, stderr not redirected
        process.communicate(prog)
        return not process.returncode
    # method try_compile
# class Main

if __name__ == '__main__':
    Main(sys.argv)
