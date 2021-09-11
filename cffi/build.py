# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import shlex
from typing import List

import cffi


HERE = os.path.dirname(__file__)

BUILDER = cffi.FFI()
with open(os.path.join(HERE, "cdefs.h"), encoding="utf-8") as f:
    BUILDER.cdef(f.read())


def search_paths(env_var: str) -> List[str]:
    paths = []
    for p in os.environ.get(env_var, "").strip().split(":"):
        p = p.strip()
        if p:
            paths.append(p)
    return paths


HEADERS = search_paths("LIBYANG_HEADERS")
LIBRARIES = search_paths("LIBYANG_LIBRARIES")
EXTRA_CFLAGS = ["-Werror", "-std=c99"]
EXTRA_CFLAGS += shlex.split(os.environ.get("LIBYANG_EXTRA_CFLAGS", ""))
EXTRA_LDFLAGS = shlex.split(os.environ.get("LIBYANG_EXTRA_LDFLAGS", ""))

with open(os.path.join(HERE, "source.c"), encoding="utf-8") as f:
    BUILDER.set_source(
        "_libyang",
        f.read(),
        libraries=["yang"],
        extra_compile_args=EXTRA_CFLAGS,
        extra_link_args=EXTRA_LDFLAGS,
        include_dirs=HEADERS,
        library_dirs=LIBRARIES,
        py_limited_api=False,
    )

if __name__ == "__main__":
    BUILDER.compile()
