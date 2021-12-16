# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import os
from typing import IO, Any, Iterator, Optional, Union

from _libyang import ffi, lib
from .data import DNode, data_format, parser_flags, path_flags, validation_flags, data_load, data_type
from .schema import Module, SNode, schema_in_format
from .util import LibyangError, c2str, str2c, IO_type, DataType


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

    def parse_module(self, in_data: Union[IO, str], in_type: IO_type, fmt: str = "yang", features=None):
        data = ffi.new("struct ly_in **")
        data_keepalive = []
        ret = data_load(in_type, in_data, data, data_keepalive)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to read input data")

        feat = ffi.NULL
        if features:
            feat = ffi.new(f"char *[{len(features) + 1}]")
            features = [str2c(i) for i in features]
            for i, val in enumerate(features):
                feat[i] = val
            feat[len(features)] = ffi.NULL

        mod = ffi.new("struct lys_module **")
        fmt = schema_in_format(fmt)
        if lib.lys_parse(self.cdata, data[0], fmt, feat, mod) != lib.LY_SUCCESS:
            raise self.error("failed to parse module")

        return Module(self, mod[0])

    def parse_module_file(self, fileobj: IO, fmt: str = "yang", features=None) -> Module:
        return self.parse_module(fileobj, IO_type.FILE, fmt, features)

    def parse_module_str(self, s: str, fmt: str = "yang", features=None) -> Module:
        return self.parse_module(s, IO_type.MEMORY, fmt, features)

    def load_module(self, name: str) -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_load_module(self.cdata, str2c(name), ffi.NULL, ffi.NULL)
        if mod == ffi.NULL:
            raise self.error("cannot load module")

        return Module(self, mod)

    def get_module(self, name: str) -> Module:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_get_module_latest(self.cdata, str2c(name))
        if mod == ffi.NULL:
            raise self.error("cannot get module")

        return Module(self, mod)

    def find_path(self, path: str, output: bool = False) -> Iterator[SNode]:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")

        flags = 0
        if output:
            flags |= lib.LYS_FIND_XP_OUTPUT

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

    def find_jsonpath(self, path: str, root_node: Optional["libyang.SNode"] = None,
                  output: bool = False) -> Optional["libyang.SNode"]:
        if root_node is not None:
            ctx_node = root_node.cdata
        else:
            ctx_node = ffi.NULL

        ret = lib.lys_find_path(self.cdata, ctx_node, str2c(path), output)
        if ret == ffi.NULL:
            return
        return SNode.new(self, ret)

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
        parent: DNode = None
    ) -> DNode:
        fmt = data_format(fmt)
        data = ffi.new("struct ly_in **")
        data_keepalive = []
        dtype = data_type(dtype)
        ret = data_load(in_type, in_data, data, data_keepalive)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to read input data")

        tree = ffi.new("struct lyd_node **")
        op = ffi.new("struct lyd_node **", ffi.NULL)
        par = ffi.new("struct lyd_node **", ffi.NULL)
        if parent is not None:
            par[0] = parent.cdata

        ret = lib.lyd_parse_op(self.cdata, par[0], data[0], fmt, dtype, tree, op)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to parse input data")

        return DNode.new(self, op[0])

    def parse_op_mem(self, fmt: str, data: str, dtype: DataType = DataType.DATA_YANG, parent: DNode = None):
        return self.parse_op(fmt, in_type=IO_type.MEMORY, in_data=data, dtype=dtype, parent=parent)

    def parse_data(  # pylint: disable=too-many-arguments
        self,
        fmt: str,
        in_type: IO_type,
        in_data: Union[str, bytes, IO],
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
        encode = True
        if fmt == lib.LYD_LYB:
            encode = False
        data = ffi.new("struct ly_in **")
        data_keepalive = []
        ret = data_load(in_type, in_data, data, data_keepalive, encode)
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
        data: Union[str, bytes],
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
        return self.parse_data(fmt,
                               in_type=IO_type.MEMORY,
                               in_data=data,
                               parser_lyb_mod_update=parser_lyb_mod_update,
                               parser_no_state=parser_no_state,
                               parser_parse_only=parser_parse_only,
                               parser_opaq=parser_opaq,
                               parser_ordered=parser_ordered,
                               parser_strict=parser_strict,
                               validation_no_state=validation_no_state,
                               validation_validate_present=validation_validate_present
                               )

    def parse_data_file(
        self,
        fileobj: IO,
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

        return self.parse_data(fmt,
                               in_type=IO_type.FD,
                               in_data=fileobj,
                               parser_lyb_mod_update=parser_lyb_mod_update,
                               parser_no_state=parser_no_state,
                               parser_parse_only=parser_parse_only,
                               parser_opaq=parser_opaq,
                               parser_ordered=parser_ordered,
                               parser_strict=parser_strict,
                               validation_no_state=validation_no_state,
                               validation_validate_present=validation_validate_present
                               )

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
