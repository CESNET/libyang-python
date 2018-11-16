#!/usr/bin/env python
# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import multiprocessing
import os
import subprocess
import sys
from distutils import log
from distutils.command.build import build
from distutils.command.build_clib import build_clib

import setuptools
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install


REQUIREMENTS = ['cffi>=1.11.5']
HERE = os.path.abspath(os.path.dirname(__file__))


class BuildCLib(build_clib):

    def run(self):
        if not self.libraries:
            return
        log.info('Building libyang C library ...')
        tmp = os.path.abspath(self.build_temp)
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        commands = [
            [
                'cmake', os.path.join(HERE, 'clib'),
                '-DCMAKE_BUILD_TYPE=release',
                '-DENABLE_STATIC=ON',
                '-DCMAKE_C_FLAGS=-fPIC',
                '-DENABLE_BUILD_TESTS=OFF',
                '-DENABLE_VALGRIND_TESTS=OFF',
                '-DCMAKE_INSTALL_PREFIX=%s' % os.path.abspath(self.build_clib),
                '-DGEN_LANGUAGE_BINDINGS=0',
            ],
            ['make', '-j%d' % multiprocessing.cpu_count()],
            ['make', 'install'],
        ]
        for cmd in commands:
            log.debug('%s$ %s', tmp, ' '.join(cmd))
            subprocess.check_call(cmd, cwd=tmp)

    def get_library_names(self):
        if not self.libraries:
            return []
        return ['pcre', 'metadata', 'yangdata', 'nacm', 'user_date_and_time']

class BuildExt(build_ext):

    def run(self):
        if self.distribution.has_c_libraries():
            c = self.get_finalized_command('build_clib')
            self.include_dirs.append(
                os.path.join(c.build_clib, 'include'))
        return build_ext.run(self)


def keywords_with_side_effects(argv):
    no_setup_requires_arguments = (
        '-h', '--help',
        '-n', '--dry-run',
        '-q', '--quiet',
        '-v', '--verbose',
        '-V', '--version',
        '--author', '--author-email',
        '--classifiers', '--contact', '--contact-email',
        '--description', '--egg-base', '--fullname', '--help-commands',
        '--keywords', '--licence', '--license',
        '--long-description', '--maintainer', '--maintainer-email',
        '--name', '--no-user-cfg', '--obsoletes', '--platforms',
        '--provides', '--requires', '--url',
        'clean', 'egg_info', 'register', 'sdist', 'upload',
    )

    def is_short_option(argument):
        """Check whether a command line argument is a short option."""
        return len(argument) >= 2 and argument[0] == '-' and argument[1] != '-'

    def expand_short_options(argument):
        """Expand combined short options into canonical short options."""
        return ('-' + char for char in argument[1:])

    def arg_without_setup_reqs(argv, i):
        """Check whether a command line argument needs setup requirements."""
        if argv[i] in no_setup_requires_arguments:
            # Simple case: An argument which is either an option or a command
            # which doesn't need setup requirements.
            return True
        elif (is_short_option(argv[i]) and
              all(option in no_setup_requires_arguments
                  for option in expand_short_options(argv[i]))):
            # Not so simple case: Combined short options none of which need
            # setup requirements.
            return True
        elif argv[i - 1:i] == ['--egg-base']:
            # Tricky case: --egg-info takes an argument which should not make
            # us use setup_requires (defeating the purpose of this code).
            return True

        return False

    if all(arg_without_setup_reqs(argv, i) for i in range(1, len(argv))):
        err_msg = ('Requested setup command that needs "setup_requires"'
                   'while command line arguments implied a side effect '
                   'free command or option.')
        class DummyBuild(build):
            def run(self):
                raise RuntimeError(err_msg)
        class DummyInstall(install):
            def run(self):
                raise RuntimeError(err_msg)
        return {
            'cmdclass': {
                'build': DummyBuild,
                'install': DummyInstall,
            },
        }
    else:
        libs = []
        if os.environ.get('LIBYANG_INSTALL') != 'system':
            libs.append(('yang', {'sources': ['clib']}))
        return {
            'setup_requires': REQUIREMENTS,
            'cffi_modules': ['cffi/build.py:BUILDER'],
            'libraries': libs,
            'cmdclass': {
                'build_clib': BuildCLib,
                'build_ext': BuildExt,
            },
        }


with open('README.rst', 'r') as f:
    LONG_DESC = f.read()


setuptools.setup(
    name='libyang',
    version='0.16.65.post1',
    description='CFFI bindings to libyang',
    long_description=LONG_DESC,
    url='https://github.com/rjarry/libyang-python',
    license='MIT',
    author='Robin Jarry',
    author_email='robin@jarry.cc',
    keywords=['libyang', 'cffi'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=REQUIREMENTS,
    packages=['libyang'],
    zip_safe=False,
    include_package_data=True,
    **keywords_with_side_effects(sys.argv)
)
