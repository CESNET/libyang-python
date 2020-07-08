# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import warnings

from _libyang import ffi


# -------------------------------------------------------------------------------------
class LibyangError(Exception):
    pass


# -------------------------------------------------------------------------------------
def deprecated(old, new, removed_in):
    msg = "%s has been replaced by %s, it will be removed in version %s"
    msg %= (old, new, removed_in)
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


# -------------------------------------------------------------------------------------
def str2c(s, encode=True):
    if s is None:
        return ffi.NULL
    if hasattr(s, "encode"):
        s = s.encode("utf-8")
    return ffi.new("char []", s)


# -------------------------------------------------------------------------------------
def c2str(c, decode=True):
    if c == ffi.NULL:
        return None
    s = ffi.string(c)
    if hasattr(s, "decode"):
        s = s.decode("utf-8")
    return s
