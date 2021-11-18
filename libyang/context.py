# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import os
from typing import IO, Any, Iterator, Optional, Union

from _libyang import ffi, lib
from .data import DNode, data_format, parser_flags, path_flags, validation_flags, data_load, data_type
from .schema import Module, SNode, schema_in_format
from .util import LibyangError, c2str, deprecated, str2c, IO_type, DataType


# -------------------------------------------------------------------------------------
class Context:

    __slots__ = ("cdata",)

    def __init__(
        self,
        search_path: Optional[str] = None,
        disable_searchdir_cwd: bool = True,
        set_priv_parsed: bool = True,
        cdata=None,  # C type: "struct ly_ctx *"
    ):
        if cdata is not None:
            self.cdata = ffi.cast("struct ly_ctx *", cdata)
            return  # already initialized

        options = 0
        if disable_searchdir_cwd:
            options |= lib.LY_CTX_DISABLE_SEARCHDIR_CWD
        if set_priv_parsed:
            options |= lib.LY_CTX_SET_PRIV_PARSED

        ctx = ffi.new("struct ly_ctx **")

        if lib.ly_ctx_new(ffi.NULL, options, ctx) != lib.LY_SUCCESS:
            #NOTE: Make errors in more detail with log information.
            raise self.error("cannot create context")

        self.cdata = ffi.gc(
            ctx[0],
            lambda ctx: lib.ly_ctx_destroy(ctx),
        )
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
            if hasattr(ffi, "release"):
                ffi.release(self.cdata)  # causes ly_ctx_destroy to be called
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
        mod = lib.ly_ctx_load_module(self.cdata, str2c(name), ffi.NULL, ffi.NULL)
        if not mod:
            raise self.error("cannot load module")

        return Module(self, mod)

    def get_module(self, name: str) -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_get_module(self.cdata, str2c(name), ffi.NULL)
        if not mod:
            raise self.error("cannot get module")

        return Module(self, mod)

    def find_path(self, path: str) -> Iterator[SNode]:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")

        node_set = ffi.new("struct ly_set **")
        if lib.lys_find_xpath(self.cdata, ffi.NULL, str2c(path), 0, node_set) != lib.LY_SUCCESS:
            raise self.error("cannot find path")

        node_set = node_set[0]
        if node_set.count == 0:
            raise self.error("cannot find path")
        try:
            for i in range(node_set.count):
                yield SNode.new(self, node_set.snodes[i])
        finally:
            lib.ly_set_free(node_set, ffi.NULL)

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
        if value is not None:
            if isinstance(value, bool):
                value = str(value).lower()
            elif not isinstance(value, str):
                value = str(value)
        flags = path_flags(
            update=update, no_parent_ret=no_parent_ret, rpc_output=rpc_output
        )
        dnode = ffi.new("struct lyd_node **")
        ret = lib.lyd_new_path(
            parent.cdata if parent else ffi.NULL,
            self.cdata,
            str2c(path),
            str2c(value),
            flags,
            dnode
        )
        dnode = dnode[0]
        if ret != lib.LY_SUCCESS:
            if lib.ly_vecode(self.cdata) != lib.LYVE_SUCCESS:
                raise self.error("cannot create data path: %s", path)
            lib.ly_err_clean(self.cdata, ffi.NULL)
        if not dnode and not force_return_value:
            return None

        if not dnode and parent:
            # This can happen when path points to an already created leaf and
            # its value does not change.
            # In that case, lookup the existing leaf and return it.
            node_set = ffi.new("struct ly_set **")
            ret = lib.lyd_find_xpath(parent.cdata, str2c(path), node_set)
            if ret != lib.LY_SUCCESS:
                raise self.error("cannot find path: %s", path)

            node_set = node_set[0]
            try:
                if not node_set or not node_set.count:
                    raise self.error("cannot find path: %s", path)
                dnode = node_set.set.s[0]
            finally:
                lib.ly_set_free(node_set, ffi.NULL)

        if not dnode:
            raise self.error("cannot find created path")

        return DNode.new(self, dnode)

    def parse_op(
        self,
        fmt: str,
        in_type: IO_type,
        in_data: Union[IO, str],
        dtype: DataType,
    ) -> DNode:
        fmt = data_format(fmt)
        data = ffi.new("struct ly_in **")
        data_keepalive = []
        dtype = data_type(dtype)
        ret = data_load(in_type, in_data, data, data_keepalive)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to read input data")

        tree = ffi.new("struct lyd_node **")
        op = ffi.new("struct lyd_node **")
        ret = lib.lyd_parse_op(self.cdata, ffi.NULL, data[0], fmt, dtype, tree, op)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to parse input data")

        return DNode.new(self, op[0])

    def parse_data(  # pylint: disable=too-many-arguments
        self,
        fmt: str,
        in_type: IO_type,
        in_data: Union[IO, str],
        parser_lyb_mod_update: bool = False,
        parser_no_state: bool = False,
        parser_parse_only: bool = False,
        parser_opaq: bool = False,
        parser_ordered: bool = False,
        parser_strict: bool = False,
        validation_no_state: bool = False,
        validation_validate_present: bool = False
    ) -> DNode:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        parser_flgs = parser_flags(
            lyb_mod_update=parser_lyb_mod_update,
            no_state=parser_no_state,
            parse_only=parser_parse_only,
            opaq=parser_opaq,
            ordered=parser_ordered,
            strict=parser_strict
        )
        validation_flgs = validation_flags(
            no_state=validation_no_state,
            validate_present=validation_validate_present
        )
        fmt = data_format(fmt)
        data = ffi.new("struct ly_in **")

        data_keepalive = []
        ret = data_load(in_type, in_data, data, data_keepalive)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to read input data")

        dnode = ffi.new("struct lyd_node **")
        ret = lib.lyd_parse_data(self.cdata, ffi.NULL, data[0], fmt, parser_flgs, validation_flgs, dnode)
        lib.ly_in_free(data[0], 0)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to parse data tree")

        dnode = dnode[0]
        return DNode.new(self, dnode)

    def parse_data_mem(  # pylint: disable=too-many-arguments
        self,
        d: Union[str, bytes],
        fmt: str,
        parser_lyb_mod_update: bool = False,
        parser_no_state: bool = False,
        parser_parse_only: bool = False,
        parser_opaq: bool = False,
        parser_ordered: bool = False,
        parser_strict: bool = False,
        validation_no_state: bool = False,
        validation_validate_present: bool = False
    ) -> DNode:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        parser_flgs = parser_flags(
            lyb_mod_update=parser_lyb_mod_update,
            no_state=parser_no_state,
            parse_only=parser_parse_only,
            opaq=parser_opaq,
            ordered=parser_ordered,
            strict=parser_strict
        )
        validation_flgs = validation_flags(
            no_state=validation_no_state,
            validate_present=validation_validate_present
        )
        fmt = data_format(fmt)
        if fmt == lib.LYD_LYB:
            d = str2c(d, encode=False)
        else:
            d = str2c(d, encode=True)
        dnode = ffi.new("struct lyd_node **")
        ret = lib.lyd_parse_data_mem(self.cdata, d, fmt, parser_flgs, validation_flgs, dnode)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to parse data tree")
        dnode = dnode[0]
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
