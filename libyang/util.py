# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

from typing import Optional
import enum
import warnings

from _libyang import ffi


# -------------------------------------------------------------------------------------
class LibyangError(Exception):
    pass


# -------------------------------------------------------------------------------------
def deprecated(old: str, new: str, removed_in: str) -> None:
    msg = "%s has been replaced by %s, it will be removed in version %s"
    msg %= (old, new, removed_in)
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


# -------------------------------------------------------------------------------------
def str2c(s: Optional[str], encode: bool = True):
    if s is None:
        return ffi.NULL
    if hasattr(s, "encode"):
        s = s.encode("utf-8")
    return ffi.new("char []", s)


# -------------------------------------------------------------------------------------
def c2str(c, decode: bool = True):
    if c == ffi.NULL:  # C type: "char *"
        return None
    s = ffi.string(c)
    if hasattr(s, "decode"):
        s = s.decode("utf-8")
    return s


# -------------------------------------------------------------------------------------
def p_str2c(s: Optional[str], encode: bool = True):
    s_p = str2c(s, encode)
    return ffi.new("char **", s_p)


# -------------------------------------------------------------------------------------
class IO_type(enum.Enum):
    FD = enum.auto()
    FILE = enum.auto()
    FILEPATH = enum.auto()
    MEMORY = enum.auto()


class DataType(enum.Enum):
    DATA_YANG = enum.auto()
    RPC_YANG = enum.auto()
    NOTIF_YANG = enum.auto()
    REPLY_YANG = enum.auto()
    RPC_NETCONF = enum.auto()
    NOTIF_NETCONF = enum.auto()
    REPLY_NETCONF = enum.auto()
