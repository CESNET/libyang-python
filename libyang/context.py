# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import os
from typing import IO, Any, Iterator, Optional, Union

from _libyang import ffi, lib
from .data import DNode, data_format, parser_flags, path_flags
from .schema import Module, SNode, schema_in_format
from .util import LibyangError, c2str, deprecated, str2c


# -------------------------------------------------------------------------------------
class Context:

    __slots__ = ("cdata",)

    def __init__(
        self,
        search_path: Optional[str] = None,
        disable_searchdir_cwd: bool = True,
        pointer=None,  # C type: "struct ly_ctx *"
        cdata=None,  # C type: "struct ly_ctx *"
    ):
        if pointer is not None:
            deprecated("pointer=", "cdata=", "2.0.0")
            cdata = pointer
        if cdata is not None:
            self.cdata = ffi.cast("struct ly_ctx *", cdata)
            return  # already initialized

        options = 0
        if disable_searchdir_cwd:
            options |= lib.LY_CTX_DISABLE_SEARCHDIR_CWD

        self.cdata = lib.ly_ctx_new(ffi.NULL, options)
        if not self.cdata:
            raise self.error("cannot create context")

        search_dirs = []
        if "YANGPATH" in os.environ:
            search_dirs.extend(os.environ["YANGPATH"].strip(": \t\r\n'\"").split(":"))
        elif "YANG_MODPATH" in os.environ:
            search_dirs.extend(
                os.environ["YANG_MODPATH"].strip(": \t\r\n'\"").split(":")
            )
        if search_path:
            search_dirs.extend(search_path.strip(": \t\r\n'\"").split(":"))

        for path in search_dirs:
            if not os.path.isdir(path):
                continue
            if lib.ly_ctx_set_searchdir(self.cdata, str2c(path)) != 0:
                raise self.error("cannot set search dir")

    @property
    def _ctx(self):
        deprecated("_ctx", "cdata", "2.0.0")
        return self.cdata

    def destroy(self):
        if self.cdata is not None:
            lib.ly_ctx_destroy(self.cdata, ffi.NULL)
            self.cdata = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.destroy()

    def error(self, msg: str, *args) -> LibyangError:
        msg %= args

        if self.cdata:
            err = lib.ly_err_first(self.cdata)
            while err:
                if err.msg:
                    msg += ": %s" % c2str(err.msg)
                if err.path:
                    msg += ": %s" % c2str(err.path)
                err = err.next
            lib.ly_err_clean(self.cdata, ffi.NULL)

        return LibyangError(msg)

    def parse_module_file(self, fileobj: IO, fmt: str = "yang") -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        fmt = schema_in_format(fmt)
        mod = lib.lys_parse_fd(self.cdata, fileobj.fileno(), fmt)
        if not mod:
            raise self.error("cannot parse module")

        return Module(self, mod)

    def parse_module_str(self, s: str, fmt: str = "yang") -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        fmt = schema_in_format(fmt)
        mod = lib.lys_parse_mem(self.cdata, str2c(s), fmt)
        if not mod:
            raise self.error("cannot parse module")

        return Module(self, mod)

    def load_module(self, name: str) -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_load_module(self.cdata, str2c(name), ffi.NULL)
        if not mod:
            raise self.error("cannot load module")

        return Module(self, mod)

    def get_module(self, name: str) -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_get_module(self.cdata, str2c(name), ffi.NULL, False)
        if not mod:
            raise self.error("cannot get module")

        return Module(self, mod)

    def find_path(self, path: str) -> Iterator[SNode]:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        node_set = lib.ly_ctx_find_path(self.cdata, str2c(path))
        if not node_set:
            raise self.error("cannot find path")
        try:
            for i in range(node_set.number):
                yield SNode.new(self, node_set.set.s[i])
        finally:
            lib.ly_set_free(node_set)

    def create_data_path(
        self,
        path: str,
        parent: Optional[DNode] = None,
        value: Any = None,
        update: bool = True,
        no_parent_ret: bool = True,
        rpc_output: bool = False,
        force_return_value: bool = True,
    ) -> Optional[DNode]:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        lib.lypy_set_errno(0)
        if value is not None:
            if isinstance(value, bool):
                value = str(value).lower()
            elif not isinstance(value, str):
                value = str(value)
        flags = path_flags(
            update=update, no_parent_ret=no_parent_ret, rpc_output=rpc_output
        )
        dnode = lib.lyd_new_path(
            parent.cdata if parent else ffi.NULL,
            self.cdata,
            str2c(path),
            str2c(value),
            0,
            flags,
        )
        if lib.lypy_get_errno() != lib.LY_SUCCESS:
            if lib.ly_vecode(self.cdata) != lib.LYVE_PATH_EXISTS:
                raise self.error("cannot create data path: %s", path)
            lib.ly_err_clean(self.cdata, ffi.NULL)
            lib.lypy_set_errno(0)
        if not dnode and not force_return_value:
            return None

        if not dnode and parent:
            # This can happen when path points to an already created leaf and
            # its value does not change.
            # In that case, lookup the existing leaf and return it.
            node_set = lib.lyd_find_path(parent.cdata, str2c(path))
            try:
                if not node_set or not node_set.number:
                    raise self.error("cannot find path: %s", path)
                dnode = node_set.set.s[0]
            finally:
                lib.ly_set_free(node_set)

        if not dnode:
            raise self.error("cannot find created path")

        return DNode.new(self, dnode)

    def parse_data_mem(
        self,
        d: Union[str, bytes],
        fmt: str,
        data: bool = False,
        config: bool = False,
        get: bool = False,
        getconfig: bool = False,
        edit: bool = False,
        rpc: bool = False,
        rpcreply: bool = False,
        strict: bool = False,
        trusted: bool = False,
        no_yanglib: bool = False,
        rpc_request: Optional[DNode] = None,
        data_tree: Optional[DNode] = None,
    ) -> DNode:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        flags = parser_flags(
            data=data,
            config=config,
            get=get,
            getconfig=getconfig,
            edit=edit,
            rpc=rpc,
            rpcreply=rpcreply,
            strict=strict,
            trusted=trusted,
            no_yanglib=no_yanglib,
        )
        fmt = data_format(fmt)
        if fmt == lib.LYD_LYB:
            d = str2c(d, encode=False)
        else:
            d = str2c(d, encode=True)
        args = []
        if rpcreply:
            if rpc_request is None:
                raise ValueError("rpc_request node is required when rpcreply=True")
            args.append(rpc_request.cdata)
        if rpc or rpcreply:
            if data_tree is not None:
                args.append(data_tree.cdata)
            else:
                args.append(ffi.cast("struct lyd_node *", ffi.NULL))
        dnode = lib.lyd_parse_mem(self.cdata, d, fmt, flags, *args)
        if not dnode:
            raise self.error("failed to parse data tree")
        return DNode.new(self, dnode)

    def parse_data_file(
        self,
        fileobj: IO,
        fmt: str,
        data: bool = False,
        config: bool = False,
        get: bool = False,
        getconfig: bool = False,
        edit: bool = False,
        rpc: bool = False,
        rpcreply: bool = False,
        strict: bool = False,
        trusted: bool = False,
        no_yanglib: bool = False,
        rpc_request: Optional[DNode] = None,
        data_tree: Optional[DNode] = None,
    ) -> DNode:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        flags = parser_flags(
            data=data,
            config=config,
            get=get,
            getconfig=getconfig,
            edit=edit,
            rpc=rpc,
            rpcreply=rpcreply,
            strict=strict,
            trusted=trusted,
            no_yanglib=no_yanglib,
        )
        fmt = data_format(fmt)
        args = []
        if rpcreply:
            if rpc_request is None:
                raise ValueError("rpc_request node is required when rpcreply=True")
            args.append(rpc_request.cdata)
        if rpc or rpcreply:
            if data_tree is not None:
                args.append(data_tree.cdata)
            else:
                args.append(ffi.cast("struct lyd_node *", ffi.NULL))
        dnode = lib.lyd_parse_fd(self.cdata, fileobj.fileno(), fmt, flags, *args)
        if not dnode:
            raise self.error("failed to parse data tree")
        return DNode.new(self, dnode)

    def __iter__(self) -> Iterator[Module]:
        """
        Return an iterator that yields all implemented modules from the context
        """
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        idx = ffi.new("uint32_t *")
        mod = lib.ly_ctx_get_module_iter(self.cdata, idx)
        while mod:
            yield Module(self, mod)
            mod = lib.ly_ctx_get_module_iter(self.cdata, idx)
