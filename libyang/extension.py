# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

from typing import Callable, Optional

from _libyang import ffi, lib
from .context import Context
from .log import get_libyang_level
from .schema import ExtensionCompiled, ExtensionParsed, Module
from .util import LibyangError, c2str, str2c


# -------------------------------------------------------------------------------------
extensions_plugins = {}


class LibyangExtensionError(LibyangError):
    def __init__(self, message: str, ret: int, log_level: int) -> None:
        super().__init__(message)
        self.ret = ret
        self.log_level = log_level


@ffi.def_extern(name="lypy_lyplg_ext_parse_clb")
def libyang_c_lyplg_ext_parse_clb(pctx, pext):
    plugin = extensions_plugins[pext.record.plugin]
    module_cdata = lib.lyplg_ext_parse_get_cur_pmod(pctx).mod
    context = Context(cdata=module_cdata.ctx)
    module = Module(context, module_cdata)
    parsed_ext = ExtensionParsed(context, pext, module)
    plugin.set_parse_ctx(pctx)
    try:
        plugin.parse_clb(module, parsed_ext)
        return lib.LY_SUCCESS
    except LibyangExtensionError as e:
        ly_level = get_libyang_level(e.log_level)
        if ly_level is None:
            ly_level = lib.LY_EPLUGIN
        e_str = str(e)
        plugin.add_error_message(e_str)
        lib.lyplg_ext_parse_log(pctx, pext, ly_level, e.ret, str2c(e_str))
        return e.ret


@ffi.def_extern(name="lypy_lyplg_ext_compile_clb")
def libyang_c_lyplg_ext_compile_clb(cctx, pext, cext):
    plugin = extensions_plugins[pext.record.plugin]
    context = Context(cdata=lib.lyplg_ext_compile_get_ctx(cctx))
    module = Module(context, cext.module)
    parsed_ext = ExtensionParsed(context, pext, module)
    compiled_ext = ExtensionCompiled(context, cext)
    plugin.set_compile_ctx(cctx)
    try:
        plugin.compile_clb(parsed_ext, compiled_ext)
        return lib.LY_SUCCESS
    except LibyangExtensionError as e:
        ly_level = get_libyang_level(e.log_level)
        if ly_level is None:
            ly_level = lib.LY_EPLUGIN
        e_str = str(e)
        plugin.add_error_message(e_str)
        lib.lyplg_ext_compile_log(cctx, cext, ly_level, e.ret, str2c(e_str))
        return e.ret


@ffi.def_extern(name="lypy_lyplg_ext_parse_free_clb")
def libyang_c_lyplg_ext_parse_free_clb(ctx, pext):
    plugin = extensions_plugins[pext.record.plugin]
    context = Context(cdata=ctx)
    parsed_ext = ExtensionParsed(context, pext, None)
    plugin.parse_free_clb(parsed_ext)


@ffi.def_extern(name="lypy_lyplg_ext_compile_free_clb")
def libyang_c_lyplg_ext_compile_free_clb(ctx, cext):
    plugin = extensions_plugins[getattr(cext, "def").plugin]
    context = Context(cdata=ctx)
    compiled_ext = ExtensionCompiled(context, cext)
    plugin.compile_free_clb(compiled_ext)


class ExtensionPlugin:
    ERROR_SUCCESS = lib.LY_SUCCESS
    ERROR_MEM = lib.LY_EMEM
    ERROR_INVALID_INPUT = lib.LY_EINVAL
    ERROR_NOT_VALID = lib.LY_EVALID
    ERROR_DENIED = lib.LY_EDENIED
    ERROR_NOT = lib.LY_ENOT

    def __init__(
        self,
        module_name: str,
        name: str,
        id_str: str,
        context: Optional[Context] = None,
        parse_clb: Optional[Callable[[Module, ExtensionParsed], None]] = None,
        compile_clb: Optional[
            Callable[[ExtensionParsed, ExtensionCompiled], None]
        ] = None,
        parse_free_clb: Optional[Callable[[ExtensionParsed], None]] = None,
        compile_free_clb: Optional[Callable[[ExtensionCompiled], None]] = None,
    ) -> None:
        """
        Set the callback functions, which will be called if libyang will be processing
        given extension defined by name from module defined by module_name.

        :arg self:
            This instance of extension plugin
        :arg module_name:
            The name of module in which the extension is defined
        :arg name:
            The name of extension itself
        :arg id_str:
            The unique ID of extension plugin within the libyang context
        :arg context:
            The context in which the extension plugin will be used. If set to None,
            the plugin will be used for all existing and even future contexts
        :arg parse_clb:
            The optional callback function of which will be called during extension parsing
            Expected arguments are:
                module: The module which is being parsed
                extension: The exact extension instance
            Expected raises:
                LibyangExtensionError in case of processing error
        :arg compile_clb:
            The optional callback function of which will be called during extension compiling
            Expected arguments are:
                extension_parsed: The parsed extension instance
                extension_compiled: The compiled extension instance
            Expected raises:
                LibyangExtensionError in case of processing error
        :arg parse_free_clb
            The optional callback function of which will be called during freeing of parsed extension
            Expected arguments are:
                extension: The parsed extension instance to be freed
        :arg compile_free_clb
            The optional callback function of which will be called during freeing of compiled extension
            Expected arguments are:
                extension: The compiled extension instance to be freed
        """
        self.context = context
        self.module_name = module_name
        self.module_name_cstr = str2c(self.module_name)
        self.name = name
        self.name_cstr = str2c(self.name)
        self.id_str = id_str
        self.id_cstr = str2c(self.id_str)
        self.parse_clb = parse_clb
        self.compile_clb = compile_clb
        self.parse_free_clb = parse_free_clb
        self.compile_free_clb = compile_free_clb
        self._error_messages = []
        self._pctx = ffi.NULL
        self._cctx = ffi.NULL

        self.cdata = ffi.new("struct lyplg_ext_record[2]")
        self.cdata[0].module = self.module_name_cstr
        self.cdata[0].name = self.name_cstr
        self.cdata[0].plugin.id = self.id_cstr
        if self.parse_clb is not None:
            self.cdata[0].plugin.parse = lib.lypy_lyplg_ext_parse_clb
        if self.compile_clb is not None:
            self.cdata[0].plugin.compile = lib.lypy_lyplg_ext_compile_clb
        if self.parse_free_clb is not None:
            self.cdata[0].plugin.pfree = lib.lypy_lyplg_ext_parse_free_clb
        if self.compile_free_clb is not None:
            self.cdata[0].plugin.cfree = lib.lypy_lyplg_ext_compile_free_clb
        ret = lib.lyplg_add_extension_plugin(
            context.cdata if context is not None else ffi.NULL,
            lib.LYPLG_EXT_API_VERSION,
            ffi.cast("const void *", self.cdata),
        )
        if ret != lib.LY_SUCCESS:
            raise LibyangError("Unable to add extension plugin")
        if self.cdata[0].plugin not in extensions_plugins:
            extensions_plugins[self.cdata[0].plugin] = self

    def __del__(self) -> None:
        if self.cdata[0].plugin in extensions_plugins:
            del extensions_plugins[self.cdata[0].plugin]

    @staticmethod
    def stmt2str(stmt: int) -> str:
        return c2str(lib.lyplg_ext_stmt2str(stmt))

    def add_error_message(self, err_msg: str) -> None:
        self._error_messages.append(err_msg)

    def clear_error_messages(self) -> None:
        self._error_messages.clear()

    def set_parse_ctx(self, pctx) -> None:
        self._pctx = pctx

    def set_compile_ctx(self, cctx) -> None:
        self._cctx = cctx

    def parse_substmts(self, ext: ExtensionParsed) -> int:
        return lib.lyplg_ext_parse_extension_instance(self._pctx, ext.cdata)

    def compile_substmts(self, pext: ExtensionParsed, cext: ExtensionCompiled) -> int:
        return lib.lyplg_ext_compile_extension_instance(
            self._cctx, pext.cdata, cext.cdata
        )

    def free_parse_substmts(self, ext: ExtensionParsed) -> None:
        lib.lyplg_ext_pfree_instance_substatements(
            self.context.cdata, ext.cdata.substmts
        )

    def free_compile_substmts(self, ext: ExtensionCompiled) -> None:
        lib.lyplg_ext_cfree_instance_substatements(
            self.context.cdata, ext.cdata.substmts
        )
