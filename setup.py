#!/usr/bin/env python
# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import datetime
from distutils import dir_util
from distutils import log
from distutils.command.build_clib import build_clib
import glob
import multiprocessing
import os
import re
import subprocess
import sys

import setuptools
from setuptools.command.build_ext import build_ext


CFFI_REQ = 'cffi>=1.7,!=1.11.3'
INSTALL_REQS = []
SETUP_REQS = []
if '_cffi_backend' not in sys.builtin_module_names:
    INSTALL_REQS.append(CFFI_REQ)
    SETUP_REQS.append(CFFI_REQ)
HERE = os.path.abspath(os.path.dirname(__file__))


class BuildCLib(build_clib):

    def run(self):
        if not self.libraries:
            return
        log.info('Building libyang C library ...')
        tmp = os.path.abspath(self.build_temp)
        cmd = [
            os.path.join(HERE, 'build-libyang.sh'),
            '--src=%s' % os.path.join(HERE, 'clib'),
            '--build=%s' % tmp,
            '--prefix=%s' % self.get_finalized_command('install').install_base,
            '--install=%s' % os.path.join(tmp, 'staging'),
        ]
        log.debug('+ %s' % ' '.join(cmd))
        subprocess.check_call(cmd)


class BuildExt(build_ext):

    def run(self):
        if self.distribution.has_c_libraries():
            if 'build_clib' not in self.distribution.have_run or \
                    not self.distribution.have_run['build_clib']:
                self.run_command('build_clib')
            tmp = os.path.abspath(
                self.get_finalized_command('build_clib').build_temp)
            self.include_dirs.append(os.path.join(tmp, 'staging/_include'))
            self.library_dirs.append(os.path.join(tmp, 'staging/_lib'))
            self.rpath.append('$ORIGIN/libyang/_lib')

        build_ext.run(self)

        if self.distribution.has_c_libraries():
            if self.inplace:
                build_py = self.get_finalized_command('build_py')
                dest = build_py.get_package_dir('libyang')
            else:
                dest = os.path.join(self.build_lib, 'libyang')
            if os.path.isdir(os.path.join(dest, '_lib')):
                # Work around dir_util.copy_tree() that fails when a symlink
                # already exists.
                for f in os.listdir(os.path.join(dest, '_lib')):
                    if os.path.islink(os.path.join(dest, '_lib', f)):
                        os.unlink(os.path.join(dest, '_lib', f))
            tmp = self.get_finalized_command('build_clib').build_temp
            dir_util.copy_tree(
                os.path.join(tmp, 'staging'), dest,
                preserve_symlinks=True, update=True)


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
