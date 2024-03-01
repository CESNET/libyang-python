# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

import enum
from typing import Optional
import warnings

from _libyang import ffi, lib


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
    if encode and hasattr(s, "encode"):
        s = s.encode("utf-8")
    return ffi.new("char []", s)


# -------------------------------------------------------------------------------------
def c2str(c, decode: bool = True):
    if c == ffi.NULL:  # C type: "char *"
        return None
    s = ffi.string(c)
    if decode and hasattr(s, "decode"):
        s = s.decode("utf-8")
    return s


# -------------------------------------------------------------------------------------
def p_str2c(s: Optional[str], encode: bool = True):
    s_p = str2c(s, encode)
    return ffi.new("char **", s_p)


# -------------------------------------------------------------------------------------
def ly_array_count(cdata):
    if cdata == ffi.NULL:
        return 0
    return ffi.cast("uint64_t *", cdata)[-1]


# -------------------------------------------------------------------------------------
def ly_array_iter(cdata):
    for i in range(ly_array_count(cdata)):
        yield cdata[i]


# -------------------------------------------------------------------------------------
def ly_list_iter(cdata):
    item = cdata
    while item != ffi.NULL:
        yield item
        item = item.next


# -------------------------------------------------------------------------------------
class IOType(enum.Enum):
    FD = enum.auto()
    FILE = enum.auto()
    FILEPATH = enum.auto()
    MEMORY = enum.auto()


# -------------------------------------------------------------------------------------
class DataType(enum.Enum):
    DATA_YANG = enum.auto()
    RPC_YANG = enum.auto()
    NOTIF_YANG = enum.auto()
    REPLY_YANG = enum.auto()
    RPC_NETCONF = enum.auto()
    NOTIF_NETCONF = enum.auto()
    REPLY_NETCONF = enum.auto()


# -------------------------------------------------------------------------------------
def init_output(out_type, out_target, out_data):
    output = None
    if out_type == IOType.FD:
        ret = lib.ly_out_new_fd(out_target.fileno(), out_data)

    elif out_type == IOType.FILE:
        ret = lib.ly_out_new_file(out_target, out_data)

    elif out_type == IOType.FILEPATH:
        out_target = str2c(out_target)
        ret = lib.ly_out_new_filepath(out_target, out_data)

    elif out_type == IOType.MEMORY:
        output = ffi.new("char **")
        ret = lib.ly_out_new_memory(output, 0, out_data)

    else:
        raise ValueError("invalid output")

    return ret, output


# -------------------------------------------------------------------------------------
def data_load(in_type, in_data, data, data_keepalive, encode=True):
    if in_type == IOType.FD:
        ret = lib.ly_in_new_fd(in_data.fileno(), data)
    elif in_type == IOType.FILE:
        ret = lib.ly_in_new_file(in_data, data)
    elif in_type == IOType.FILEPATH:
        ret = lib.ly_in_new_filepath(str2c(in_data), len(in_data), data)
    elif in_type == IOType.MEMORY:
        c_str = str2c(in_data, encode=encode)
        data_keepalive.append(c_str)
        ret = lib.ly_in_new_memory(c_str, data)
    return ret
