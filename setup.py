#!/usr/bin/env python3
# Copyright (c) 2018-2020 David Sedlák
# SPDX-License-Identifier: MIT

from setuptools import setup


def read_file(fpath, encoding="utf-8"):
    with open(fpath, "r", encoding=encoding) as f:
        return f.read().strip()


setup(name='libyang2',
      description="CFFI bindings to libyang",
      version='1.0',
      setup_requires=["cffi>=1.0.0"],
      install_requires=["cffi>=1.0.0"],
      cffi_modules=["cffi/build.py:ffibuilder"],
      packages=['libyang2'],
)
