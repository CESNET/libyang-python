# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

import os
from typing import IO, Any, Callable, Iterator, Optional, Tuple, Union

from _libyang import ffi, lib
from .data import (
    DNode,
    data_format,
    data_type,
    newval_flags,
    parser_flags,
    validation_flags,
)
from .schema import Module, SNode, schema_in_format
from .util import DataType, IOType, LibyangError, c2str, data_load, str2c


# -------------------------------------------------------------------------------------
@ffi.def_extern(name="lypy_module_imp_data_free_clb")
def libyang_c_module_imp_data_free_clb(cdata, user_data):
    instance = ffi.from_handle(user_data)
    instance.free_module_data(cdata)


# -------------------------------------------------------------------------------------
@ffi.def_extern(name="lypy_module_imp_clb")
def libyang_c_module_imp_clb(
    mod_name,
    mod_rev,
    submod_name,
    submod_rev,
    user_data,
    fmt,
    module_data,
    free_module_data,
):
    """
    Implement the C callback function for loading modules from any location.

    :arg c_str mod_name:
        The YANG module name
    :arg c_str mod_rev:
        The YANG module revision
    :arg c_str submod_name:
        The YANG submodule name
    :arg c_str submod_rev:
        The YANG submodule revision
    :arg user_data:
        The user data provided by user during registration. In this implementation
        it is always considered to be handle of Python object
    :arg fmt:
        The output pointer where to set the format of schema
    :arg module_data:
        The output pointer where to set the schema data itself
    :arg free_module_data:
        The output pointer of callback function which will be called when the schema
        data are no longer needed

    :returns:
        The LY_SUCCESS in case the needed YANG (sub)module schema was found
        The LY_ENOT in case the needed YANG (sub)module schema was not found
    """
    fmt[0] = lib.LYS_IN_UNKNOWN
    module_data[0] = ffi.NULL
    free_module_data[0] = lib.lypy_module_imp_data_free_clb
    instance = ffi.from_handle(user_data)
    ret = instance.get_module_data(
        c2str(mod_name), c2str(mod_rev), c2str(submod_name), c2str(submod_rev)
    )
    if ret is None:
        return lib.LY_ENOT
    in_fmt, content = ret
    fmt[0] = schema_in_format(in_fmt)
    module_data[0] = content
    return lib.LY_SUCCESS


# -------------------------------------------------------------------------------------
class ContextExternalModuleLoader:
    __slots__ = (
        "_cdata",
        "_module_data_clb",
        "_cffi_handle",
        "_cdata_modules",
    )

    def __init__(self, cdata) -> None:
        self._cdata = cdata  # C type: "struct ly_ctx *"
        self._module_data_clb = None
        self._cffi_handle = ffi.new_handle(self)
        self._cdata_modules = []

    def free_module_data(self, cdata) -> None:
        """
        Free previously stored data, obtained after a get_module_data.

        :arg cdata:
            The pointer to YANG modelu schema (c_str), which shall be released from memory
        """
        self._cdata_modules.remove(cdata)

    def get_module_data(
        self,
        mod_name: Optional[str],
        mod_rev: Optional[str],
        submod_name: Optional[str],
        submod_rev: Optional[str],
    ) -> Optional[Tuple[str, str]]:
        """
        Get the YANG module schema data based requirements from libyang_c_module_imp_clb
        function and forward that request to user Python based callback function.

        The returned data from callback function are stored within the context to make sure
        of no memory access issues. These data a stored until the free_module_data function
        is called directly by libyang.

        :arg self
            This instance on context
        :arg mod_name:
            The optional YANG module name
        :arg mod_rev:
            The optional YANG module revision
        :arg submod_name:
            The optional YANG submodule name
        :arg submod_rev:
            The optional YANG submodule revision

        :returns:
            Tuple of format string and YANG (sub)module schema
        """
        if self._module_data_clb is None:
            return None
        ret = self._module_data_clb(mod_name, mod_rev, submod_name, submod_rev)
        if ret is None:
            return None
        fmt_str, module_data = ret
        module_data_c = str2c(module_data)
        self._cdata_modules.append(module_data_c)
        return fmt_str, module_data_c

    def set_module_data_clb(
        self,
        clb: Optional[
            Callable[
                [Optional[str], Optional[str], Optional[str], Optional[str]],
                Optional[Tuple[str, str]],
            ]
        ] = None,
    ) -> None:
        """
        Set the callback function, which will be called if libyang context would like to
        load module or submodule, which is not locally available in context path(s).

        :arg self
            This instance on context
        :arg clb:
            The callback function. The expected arguments are:
                mod_name: Module name
                mod_rev: Module revision
                submod_name: Submodule name
                submod_rev: Submodule revision
            The expeted return value is either:
                tuple of:
                    format: The string format of the loaded data
                    data: The YANG (sub)module data as string
                or None in case of error
        """
        self._module_data_clb = clb
        if clb is None:
            lib.ly_ctx_set_module_imp_clb(self._cdata, ffi.NULL, ffi.NULL)
        else:
            lib.ly_ctx_set_module_imp_clb(
                self._cdata, lib.lypy_module_imp_clb, self._cffi_handle
            )


# -------------------------------------------------------------------------------------
class Context:
    __slots__ = (
        "cdata",
        "external_module_loader",
        "__dict__",
    )

    def __init__(
        self,
        search_path: Optional[str] = None,
        disable_searchdirs: bool = False,
        disable_searchdir_cwd: bool = True,
        explicit_compile: Optional[bool] = False,
        leafref_extended: bool = False,
        leafref_linking: bool = False,
        builtin_plugins_only: bool = False,
        yanglib_path: Optional[str] = None,
        yanglib_fmt: str = "json",
        cdata=None,  # C type: "struct ly_ctx *"
    ):
        if cdata is not None:
            self.cdata = ffi.cast("struct ly_ctx *", cdata)
            self.external_module_loader = ContextExternalModuleLoader(self.cdata)
            return  # already initialized

        options = 0
        if disable_searchdirs:
            options |= lib.LY_CTX_DISABLE_SEARCHDIRS
        if disable_searchdir_cwd:
            options |= lib.LY_CTX_DISABLE_SEARCHDIR_CWD
        if explicit_compile:
            options |= lib.LY_CTX_EXPLICIT_COMPILE
        if leafref_extended:
            options |= lib.LY_CTX_LEAFREF_EXTENDED
        if leafref_linking:
            options |= lib.LY_CTX_LEAFREF_LINKING
        if builtin_plugins_only:
            options |= lib.LY_CTX_BUILTIN_PLUGINS_ONLY
        # force priv parsed
        options |= lib.LY_CTX_SET_PRIV_PARSED

        self.cdata = None
        ctx = ffi.new("struct ly_ctx **")

        search_paths = []
        if "YANGPATH" in os.environ:
            search_paths.extend(os.environ["YANGPATH"].strip(": \t\r\n'\"").split(":"))
        elif "YANG_MODPATH" in os.environ:
            search_paths.extend(
                os.environ["YANG_MODPATH"].strip(": \t\r\n'\"").split(":")
            )
        if search_path:
            search_paths.extend(search_path.strip(": \t\r\n'\"").split(":"))

        search_paths = [path for path in search_paths if os.path.isdir(path)]
        search_path = ":".join(search_paths) if search_paths else None

        if yanglib_path is None:
            options |= lib.LY_CTX_NO_YANGLIBRARY
            if lib.ly_ctx_new(str2c(search_path), options, ctx) != lib.LY_SUCCESS:
                raise self.error("cannot create context")
        else:
            if yanglib_fmt == "json":
                fmt = lib.LYD_JSON
            else:
                fmt = lib.LYD_XML
            ret = lib.ly_ctx_new_ylpath(
                str2c(search_path), str2c(yanglib_path), fmt, options, ctx
            )
            if ret != lib.LY_SUCCESS:
                raise self.error("cannot create context")

        self.cdata = ffi.gc(
            ctx[0],
            lib.ly_ctx_destroy,
        )
        if not self.cdata:
            raise self.error("cannot create context")
        self.external_module_loader = ContextExternalModuleLoader(self.cdata)

    def compile_schema(self):
        ret = lib.ly_ctx_compile(self.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.error("could not compile schema")

    def get_yanglib_data(self, content_id_format=""):
        dnode = ffi.new("struct lyd_node **")
        ret = lib.ly_ctx_get_yanglib_data(self.cdata, dnode, str2c(content_id_format))
        if ret != lib.LY_SUCCESS:
            raise self.error("cannot get yanglib data")
        return DNode.new(self, dnode[0])

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
                if err.data_path:
                    msg += ": Data path: %s" % c2str(err.data_path)
                if err.schema_path:
                    msg += ": Schema path: %s" % c2str(err.schema_path)
                if err.line != 0:
                    msg += " (line %u)" % err.line
                err = err.next
            lib.ly_err_clean(self.cdata, ffi.NULL)

        return LibyangError(msg)

    def parse_module(
        self,
        in_data: Union[IO, str],
        in_type: IOType,
        fmt: str = "yang",
        features=None,
    ):
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

    def parse_module_file(
        self, fileobj: IO, fmt: str = "yang", features=None
    ) -> Module:
        return self.parse_module(fileobj, IOType.FILE, fmt, features)

    def parse_module_str(self, s: str, fmt: str = "yang", features=None) -> Module:
        return self.parse_module(s, IOType.MEMORY, fmt, features)

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

    def find_path(
        self,
        path: str,
        output: bool = False,
        root_node: Optional["libyang.SNode"] = None,
    ) -> Iterator[SNode]:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")

        if root_node is not None:
            ctx_node = root_node.cdata
        else:
            ctx_node = ffi.NULL

        flags = 0
        if output:
            flags |= lib.LYS_FIND_XP_OUTPUT

        node_set = ffi.new("struct ly_set **")
        if (
            lib.lys_find_xpath(self.cdata, ctx_node, str2c(path), 0, node_set)
            != lib.LY_SUCCESS
        ):
            raise self.error("cannot find path")

        node_set = node_set[0]
        if node_set.count == 0:
            raise self.error("cannot find path")
        try:
            for i in range(node_set.count):
                yield SNode.new(self, node_set.snodes[i])
        finally:
            lib.ly_set_free(node_set, ffi.NULL)

    def find_jsonpath(
        self,
        path: str,
        root_node: Optional["libyang.SNode"] = None,
        output: bool = False,
    ) -> Optional["libyang.SNode"]:
        if root_node is not None:
            ctx_node = root_node.cdata
        else:
            ctx_node = ffi.NULL

        ret = lib.lys_find_path(self.cdata, ctx_node, str2c(path), output)
        if ret == ffi.NULL:
            return None
        return SNode.new(self, ret)

    def create_data_path(
        self,
        path: str,
        parent: Optional[DNode] = None,
        value: Any = None,
        update: bool = True,
        store_only: bool = False,
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
        flags = newval_flags(
            update=update, store_only=store_only, rpc_output=rpc_output
        )
        dnode = ffi.new("struct lyd_node **")
        ret = lib.lyd_new_path(
            parent.cdata if parent else ffi.NULL,
            self.cdata,
            str2c(path),
            str2c(value),
            flags,
            dnode,
        )
        dnode = dnode[0]
        if ret != lib.LY_SUCCESS:
            err = lib.ly_err_last(self.cdata)
            if err != ffi.NULL and err.vecode != lib.LYVE_SUCCESS:
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
                dnode = node_set.dnodes[0]
            finally:
                lib.ly_set_free(node_set, ffi.NULL)

        if not dnode:
            raise self.error("cannot find created path")

        return DNode.new(self, dnode)

    def parse_op(
        self,
        fmt: str,
        in_type: IOType,
        in_data: Union[IO, str],
        dtype: DataType,
        parent: DNode = None,
    ) -> DNode:
        fmt = data_format(fmt)
        data = ffi.new("struct ly_in **")
        data_keepalive = []
        dtype = data_type(dtype)
        ret = data_load(in_type, in_data, data, data_keepalive)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to read input data")

        tree = ffi.new("struct lyd_node **", ffi.NULL)
        op = ffi.new("struct lyd_node **", ffi.NULL)
        par = ffi.new("struct lyd_node **", ffi.NULL)
        if parent is not None:
            par[0] = parent.cdata

        ret = lib.lyd_parse_op(self.cdata, par[0], data[0], fmt, dtype, tree, op)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to parse input data")

        return DNode.new(self, op[0])

    def parse_op_mem(
        self,
        fmt: str,
        data: str,
        dtype: DataType = DataType.DATA_YANG,
        parent: DNode = None,
    ):
        return self.parse_op(
            fmt, in_type=IOType.MEMORY, in_data=data, dtype=dtype, parent=parent
        )

    def parse_data(
        self,
        fmt: str,
        in_type: IOType,
        in_data: Union[str, bytes, IO],
        parent: DNode = None,
        lyb_mod_update: bool = False,
        no_state: bool = False,
        parse_only: bool = False,
        opaq: bool = False,
        ordered: bool = False,
        strict: bool = False,
        validate_present: bool = False,
        validate_multi_error: bool = False,
        store_only: bool = False,
    ) -> Optional[DNode]:
        if self.cdata is None:
            raise RuntimeError("context already destroyed")
        parser_flgs = parser_flags(
            lyb_mod_update=lyb_mod_update,
            no_state=no_state,
            parse_only=parse_only,
            opaq=opaq,
            ordered=ordered,
            strict=strict,
            store_only=store_only,
        )
        validation_flgs = validation_flags(
            no_state=no_state,
            validate_present=validate_present,
            validate_multi_error=validate_multi_error,
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

        if parent is not None:
            ret = lib.lyd_parse_data(
                self.cdata,
                parent.cdata,
                data[0],
                fmt,
                parser_flgs,
                validation_flgs,
                ffi.NULL,
            )
            lib.ly_in_free(data[0], 0)
            if ret != lib.LY_SUCCESS:
                raise self.error("failed to parse data tree")
            return None

        dnode = ffi.new("struct lyd_node **")
        ret = lib.lyd_parse_data(
            self.cdata, ffi.NULL, data[0], fmt, parser_flgs, validation_flgs, dnode
        )
        lib.ly_in_free(data[0], 0)
        if ret != lib.LY_SUCCESS:
            raise self.error("failed to parse data tree")

        dnode = dnode[0]
        if dnode == ffi.NULL:
            return None
        return DNode.new(self, dnode)

    def parse_data_mem(
        self,
        data: Union[str, bytes],
        fmt: str,
        parent: DNode = None,
        lyb_mod_update: bool = False,
        no_state: bool = False,
        parse_only: bool = False,
        opaq: bool = False,
        ordered: bool = False,
        strict: bool = False,
        validate_present: bool = False,
        validate_multi_error: bool = False,
        store_only: bool = False,
    ) -> Optional[DNode]:
        return self.parse_data(
            fmt,
            in_type=IOType.MEMORY,
            in_data=data,
            parent=parent,
            lyb_mod_update=lyb_mod_update,
            no_state=no_state,
            parse_only=parse_only,
            opaq=opaq,
            ordered=ordered,
            strict=strict,
            validate_present=validate_present,
            validate_multi_error=validate_multi_error,
            store_only=store_only,
        )

    def parse_data_file(
        self,
        fileobj: IO,
        fmt: str,
        parent: DNode = None,
        lyb_mod_update: bool = False,
        no_state: bool = False,
        parse_only: bool = False,
        opaq: bool = False,
        ordered: bool = False,
        strict: bool = False,
        validate_present: bool = False,
        validate_multi_error: bool = False,
        store_only: bool = False,
    ) -> Optional[DNode]:
        return self.parse_data(
            fmt,
            in_type=IOType.FD,
            in_data=fileobj,
            parent=parent,
            lyb_mod_update=lyb_mod_update,
            no_state=no_state,
            parse_only=parse_only,
            opaq=opaq,
            ordered=ordered,
            strict=strict,
            validate_present=validate_present,
            validate_multi_error=validate_multi_error,
            store_only=store_only,
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

    def add_to_dict(self, orig_str: str) -> Any:
        cstr = ffi.new("char **")
        ret = lib.lydict_insert(self.cdata, str2c(orig_str), 0, cstr)
        if ret != lib.LY_SUCCESS:
            raise LibyangError("Unable to insert string into context dictionary")
        return cstr[0]

    def remove_from_dict(self, orig_str: str) -> None:
        lib.lydict_remove(self.cdata, str2c(orig_str))
