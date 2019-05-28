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

import os
import shlex

import cffi


HERE = os.path.dirname(__file__)

BUILDER = cffi.FFI()
with open(os.path.join(HERE, 'cdefs.h')) as f:
    BUILDER.cdef(f.read())

HEADERS = []
if 'LIBYANG_HEADERS' in os.environ:
    HEADERS.append(os.environ['LIBYANG_HEADERS'])
LIBRARIES = []
if 'LIBYANG_LIBRARIES' in os.environ:
    LIBRARIES.append(os.environ['LIBYANG_LIBRARIES'])
EXTRA_CFLAGS = ['-Werror', '-std=c99']
EXTRA_CFLAGS += shlex.split(os.environ.get('LIBYANG_EXTRA_CFLAGS', ''))
EXTRA_LDFLAGS = shlex.split(os.environ.get('LIBYANG_EXTRA_LDFLAGS', ''))

with open(os.path.join(HERE, 'source.c')) as f:
    BUILDER.set_source('_libyang', f.read(), libraries=['yang'],
                       extra_compile_args=EXTRA_CFLAGS,
                       extra_link_args=EXTRA_LDFLAGS,
                       include_dirs=HEADERS,
                       library_dirs=LIBRARIES,
                       py_limited_api=False)

if __name__ == '__main__':
    BUILDER.compile()
