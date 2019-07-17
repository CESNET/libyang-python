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

import datetime
from distutils import log
from distutils.command.build_clib import build_clib
import multiprocessing
import os
import re
import subprocess
import sys

import setuptools
from setuptools.command.build_ext import build_ext


CFFI_REQ = 'cffi>=1.7,!=1.11.3'
INSTALL_REQS = []
SETUP_REQS = ['wheel']
if '_cffi_backend' not in sys.builtin_module_names:
    INSTALL_REQS.append(CFFI_REQ)
    SETUP_REQS.append(CFFI_REQ)
HERE = os.path.abspath(os.path.dirname(__file__))
CLIB_PREFIX = os.path.join(HERE, 'build', 'clib')


class BuildCLib(build_clib):

    def run(self):
        if not self.libraries:
            return
        log.info('Building libyang C library ...')
        if not os.path.exists(CLIB_PREFIX):
            os.makedirs(CLIB_PREFIX)
        commands = [
            [
                'cmake', os.path.join(HERE, 'clib'),
                '-DCMAKE_BUILD_TYPE=release',
                '-DENABLE_STATIC=ON',
                '-DCMAKE_C_FLAGS=-fPIC',
                '-DENABLE_BUILD_TESTS=OFF',
                '-DENABLE_VALGRIND_TESTS=OFF',
                '-DCMAKE_INSTALL_PREFIX=%s' % CLIB_PREFIX,
                '-DGEN_LANGUAGE_BINDINGS=0',
            ],
            ['make', '-j%d' % multiprocessing.cpu_count()],
            ['make', 'install'],
        ]
        for cmd in commands:
            log.debug('%s$ %s', CLIB_PREFIX, ' '.join(cmd))
            subprocess.check_call(cmd, cwd=CLIB_PREFIX)

    def get_library_names(self):
        if not self.libraries:
            return []
        return ['pcre', 'metadata', 'yangdata', 'nacm', 'user_date_and_time']


class BuildExt(build_ext):

    def run(self):
        if self.distribution.has_c_libraries():
            self.include_dirs.append(os.path.join(CLIB_PREFIX, 'include'))
            self.library_dirs.append(CLIB_PREFIX)
        return build_ext.run(self)


LIBRARIES = []
if os.environ.get('LIBYANG_INSTALL') != 'system':
    LIBRARIES.append(('yang', {'sources': ['clib']}))


def _tag_to_pep440_version(tag):
    git_tag_re = re.compile(r'''
        ^
        v(?P<major>\d+)\.
        (?P<minor>\d+)\.
        (?P<patch>\d+)
        (\.post(?P<post>\d+))?
        (-(?P<dev>\d+))?
        (-g(?P<commit>.+))?
        $
        ''', re.VERBOSE)

    match = git_tag_re.match(tag)
    if match:
        d = match.groupdict()
        fmt = '{major}.{minor}.{patch}'
        if d.get('post'):
            fmt += '.post{post}'
        if d.get('dev'):
            d['patch'] = int(d['patch']) + 1
            fmt += '.dev{dev}'
        return fmt.format(**d)

    return datetime.datetime.now().strftime('%Y.%m.%d')


def _tag_from_git_describe():
    if not os.path.isdir(os.path.join(HERE, '.git')):
        raise ValueError('not in git repo')

    out = subprocess.check_output(['git', 'describe', '--always'],
                                  cwd=HERE, stderr=subprocess.STDOUT)
    return out.strip().decode('utf-8')


def _version_from_git_archive_id(git_archive_id='$Format:%ct %d$'):
    if git_archive_id.startswith('$For''mat:'):
        raise ValueError('not a git archive')

    match = re.search(r'tag:\s*v([^,)]+)', git_archive_id)
    if match:
        # archived revision is tagged, use the tag
        return _tag_to_pep440_version(match.group(1))

    # archived revision is not tagged, use the commit date
    tstamp = git_archive_id.strip().split()[0]
    d = datetime.datetime.fromtimestamp(int(tstamp))


def _version():
    try:
        tag = _tag_from_git_describe()
        version = _tag_to_pep440_version(tag)
        with open(os.path.join(HERE, 'VERSION'), 'w') as f:
            f.write(version)
        return version
    except:
        pass
    try:
        with open(os.path.join(HERE, 'VERSION'), 'r') as f:
            version = f.read()
        return version.strip()
    except:
        pass
    try:
        return _version_from_git_archive_id()
    except:
        pass

    return 'latest'


setuptools.setup(
    name='libyang',
    version=_version(),
    description='CFFI bindings to libyang',
    long_description=open('README.rst').read(),
    url='https://github.com/rjarry/libyang-cffi',
    license='MIT',
    author='Robin Jarry',
    author_email='robin@jarry.cc',
    keywords=['libyang', 'cffi'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
    ],
    packages=['libyang'],
    zip_safe=False,
    include_package_data=True,
    setup_requires=SETUP_REQS,
    install_requires=INSTALL_REQS,
    cffi_modules=['cffi/build.py:BUILDER'],
    libraries=LIBRARIES,
    cmdclass={
        'build_clib': BuildCLib,
        'build_ext': BuildExt,
    },
)
