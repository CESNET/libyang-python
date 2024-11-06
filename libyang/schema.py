# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

from contextlib import suppress
from typing import IO, Any, Dict, Iterator, List, Optional, Tuple, Union

from _libyang import ffi, lib
from .util import (
    IOType,
    LibyangError,
    c2str,
    init_output,
    ly_array_iter,
    ly_list_iter,
    str2c,
)


# -------------------------------------------------------------------------------------
def schema_in_format(fmt_string: str) -> int:
    if fmt_string == "yang":
        return lib.LYS_IN_YANG
    if fmt_string == "yin":
        return lib.LYS_IN_YIN
    raise ValueError("unknown schema input format: %r" % fmt_string)


# -------------------------------------------------------------------------------------
def schema_out_format(fmt_string: str) -> int:
    if fmt_string == "yang":
        return lib.LYS_OUT_YANG
    if fmt_string == "yin":
        return lib.LYS_OUT_YIN
    if fmt_string == "tree":
        return lib.LYS_OUT_TREE
    raise ValueError("unknown schema output format: %r" % fmt_string)


# -------------------------------------------------------------------------------------
def printer_flags(
    no_substmt: bool = False,
    shrink: bool = False,
) -> int:
    flags = 0
    if no_substmt:
        flags |= lib.LYS_PRINT_NO_SUBSTMT
    if shrink:
        flags |= lib.LYS_PRINT_SHRINK
    return flags


# -------------------------------------------------------------------------------------
class Module:
    __slots__ = ("context", "cdata", "__dict__")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_module *"

    def name(self) -> str:
        return c2str(self.cdata.name)

    def prefix(self) -> str:
        return c2str(self.cdata.prefix)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def filepath(self) -> Optional[str]:
        return c2str(self.cdata.filepath)

    def implemented(self) -> bool:
        return bool(self.cdata.implemented)

    def feature_enable(self, name: str) -> None:
        p = str2c(name)
        q = ffi.new("char *[2]", [p, ffi.NULL])
        ret = lib.lys_set_implemented(self.cdata, q)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("no such feature: %r" % name)

    def feature_enable_all(self) -> None:
        self.feature_enable("*")

    def feature_disable_all(self) -> None:
        val = ffi.new("char **", ffi.NULL)
        ret = lib.lys_set_implemented(self.cdata, val)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot disable all features")

    def feature_state(self, name: str) -> bool:
        ret = lib.lys_feature_value(self.cdata, str2c(name))
        if ret == lib.LY_SUCCESS:
            return True
        if ret == lib.LY_ENOT:
            return False
        raise self.context.error("no such feature: %r" % name)

    def features(self) -> Iterator["Feature"]:
        features_list = []
        f = ffi.NULL
        idx = ffi.new("uint32_t *")
        while True:
            f = lib.lysp_feature_next(f, self.cdata.parsed, idx)
            if f == ffi.NULL:
                break
            features_list.append(f)

        for i in features_list:
            yield Feature(self.context, i)

    def get_feature(self, name: str) -> "Feature":
        for f in self.features():
            if f.name() == name:
                return f
        raise self.context.error("no such feature: %r" % name)

    def revisions(self) -> Iterator["Revision"]:
        for revision in ly_array_iter(self.cdata.parsed.revs):
            yield Revision(self.context, revision, self)

    def typedefs(self) -> Iterator["Typedef"]:
        for typedef in ly_array_iter(self.cdata.parsed.typedefs):
            yield Typedef(self.context, typedef)

    def get_typedef(self, name: str) -> Optional["Typedef"]:
        for typedef in self.typedefs():
            if typedef.name() != name:
                continue
            return typedef
        return None

    def imports(self) -> Iterator["Import"]:
        for i in ly_array_iter(self.cdata.parsed.imports):
            yield Import(self.context, i, self)

    def get_module_from_prefix(self, prefix: str) -> Optional["Module"]:
        for i in self.imports():
            if i.prefix() != prefix:
                continue
            return self.context.get_module(i.name())
        return None

    def __iter__(self) -> Iterator["SNode"]:
        return self.children()

    def children(
        self, types: Optional[Tuple[int, ...]] = None, with_choice: bool = False
    ) -> Iterator["SNode"]:
        return iter_children(
            self.context, self.cdata, types=types, with_choice=with_choice
        )

    def parsed_children(self) -> Iterator["PNode"]:
        for c in ly_list_iter(self.cdata.parsed.data):
            yield PNode.new(self.context, c, self)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata.parsed.groupings):
            yield PGrouping(self.context, g, self)

    def augments(self) -> Iterator["PAugment"]:
        for a in ly_array_iter(self.cdata.parsed.augments):
            yield PAugment(self.context, a, self)

    def actions(self) -> Iterator["PAction"]:
        for a in ly_list_iter(self.cdata.parsed.rpcs):
            yield PAction(self.context, a, self)

    def notifications(self) -> Iterator["PNotif"]:
        for n in ly_list_iter(self.cdata.parsed.notifs):
            yield PNotif(self.context, n, self)

    def __str__(self) -> str:
        return self.name()

    def print(
        self,
        fmt: str,
        out_type: IOType,
        out_target: Union[IO, str, None] = None,
        printer_no_substmt: bool = False,
        printer_shrink: bool = False,
    ) -> Union[str, bytes, None]:
        fmt = schema_out_format(fmt)
        flags = printer_flags(no_substmt=printer_no_substmt, shrink=printer_shrink)
        out_data = ffi.new("struct ly_out **")
        ret, output = init_output(out_type, out_target, out_data)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("failed to initialize output target")

        ret = lib.lys_print_module(out_data[0], self.cdata, fmt, 0, flags)
        if output is not None:
            tmp = output[0]
            output = c2str(tmp)
            lib.free(tmp)
        lib.ly_out_free(out_data[0], ffi.NULL, False)

        if ret != lib.LY_SUCCESS:
            raise self.context.error("failed to write data")

        return output

    def print_mem(
        self,
        fmt: str = "tree",
        printer_no_substmt: bool = False,
        printer_shrink: bool = False,
    ) -> Union[str, bytes]:
        return self.print(
            fmt,
            IOType.MEMORY,
            None,
            printer_no_substmt=printer_no_substmt,
            printer_shrink=printer_shrink,
        )

    def print_file(
        self,
        fileobj: IO,
        fmt: str = "tree",
        printer_no_substmt: bool = False,
        printer_shrink: bool = False,
    ) -> None:
        return self.print(
            fmt,
            IOType.FD,
            fileobj,
            printer_no_substmt=printer_no_substmt,
            printer_shrink=printer_shrink,
        )

    def parse_data_dict(
        self,
        dic: Dict[str, Any],
        no_state: bool = False,
        validate_present: bool = False,
        validate: bool = True,
        strict: bool = False,
        rpc: bool = False,
        rpcreply: bool = False,
        notification: bool = False,
        store_only: bool = False,
    ) -> "libyang.data.DNode":
        """
        Convert a python dictionary to a DNode object following the schema of this
        module. The returned value is always a top-level data node (i.e.: without
        parent).

        :arg dic:
            The python dictionary to convert.
        :arg no_state:
            Consider state data not allowed and raise an error during validation if they are found.
        :arg validate_present:
            Validate result of the operation against schema.
        :arg validate:
            Run validation on result of the operation.
        :arg strict:
            Instead of ignoring data without schema definition, raise an error.
        :arg rpc:
            Data represents RPC or action input parameters.
        :arg rpcreply:
            Data represents RPC or action output parameters.
        :arg notification:
            Data represents a NETCONF notification.
        """
        from .data import dict_to_dnode  # circular import

        return dict_to_dnode(
            dic,
            self,
            no_state=no_state,
            validate_present=validate_present,
            validate=validate,
            strict=strict,
            rpc=rpc,
            rpcreply=rpcreply,
            notification=notification,
            store_only=store_only,
        )


# -------------------------------------------------------------------------------------
class Revision:
    __slots__ = ("context", "cdata", "module", "__dict__")

    def __init__(self, context: "libyang.Context", cdata, module):
        self.context = context
        self.cdata = cdata  # C type: "struct lysp_revision *"
        self.module = module

    def date(self) -> str:
        return c2str(self.cdata.date)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def extensions(self) -> Iterator["ExtensionParsed"]:
        for ext in ly_array_iter(self.cdata.exts):
            yield ExtensionParsed(self.context, ext, self.module)

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional["ExtensionParsed"]:
        for ext in self.extensions():
            if ext.name() != name:
                continue
            if prefix is not None and ext.module().name() != prefix:
                continue
            if arg_value is not None and ext.argument() != arg_value:
                continue
            return ext
        return None

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.date()


# -------------------------------------------------------------------------------------
class Import:
    __slots__ = ("context", "cdata", "module", "__dict__")

    def __init__(self, context: "libyang.Context", cdata, module):
        self.context = context
        self.cdata = cdata  # C type: "struct lysp_import *"
        self.module = module

    def name(self) -> str:
        return c2str(self.cdata.name)

    def prefix(self) -> Optional[str]:
        return c2str(self.cdata.prefix)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def extensions(self) -> Iterator["ExtensionParsed"]:
        for ext in ly_array_iter(self.cdata.exts):
            yield ExtensionParsed(self.context, ext, self.module)

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional["ExtensionParsed"]:
        for ext in self.extensions():
            if ext.name() != name:
                continue
            if prefix is not None and ext.module().name() != prefix:
                continue
            if arg_value is not None and ext.argument() != arg_value:
                continue
            return ext
        return None

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class Extension:
    __slots__ = ("context", "cdata", "__dict__")

    def __init__(self, context: "libyang.Context", cdata, module_parent: Module = None):
        self.context = context
        self.cdata = cdata

    def argument(self) -> Optional[str]:
        return c2str(self.cdata.argument)

    def name(self) -> str:
        return str(self.cdata)

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class ExtensionParsed(Extension):
    __slots__ = ("module_parent",)

    def __init__(self, context: "libyang.Context", cdata, module_parent: Module = None):
        super().__init__(context, cdata)
        self.module_parent = module_parent

    def _module_from_parsed(self) -> Module:
        prefix = c2str(self.cdata.name).split(":")[0]
        for cdata_imp_mod in ly_array_iter(self.module_parent.cdata.parsed.imports):
            if ffi.string(cdata_imp_mod.prefix).decode() == prefix:
                return Module(self.context, cdata_imp_mod.module)
        raise self.context.error("cannot get module")

    def name(self) -> str:
        return c2str(self.cdata.name).split(":")[1]

    def module(self) -> Module:
        return self._module_from_parsed()

    def parent_node(self) -> Optional["PNode"]:
        if not bool(self.cdata.parent_stmt & lib.LY_STMT_NODE_MASK):
            return None
        try:
            return PNode.new(self.context, self.cdata.parent, self.module())
        except LibyangError:
            return None


# -------------------------------------------------------------------------------------
class ExtensionCompiled(Extension):
    __slots__ = ("cdata_def",)

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_def = getattr(cdata, "def", None)

    def name(self) -> str:
        return c2str(self.cdata_def.name)

    def module(self) -> Module:
        if not self.cdata_def.module:
            raise self.context.error("cannot get module")
        return Module(self.context, self.cdata_def.module)

    def parent_node(self) -> Optional["SNode"]:
        if not bool(self.cdata.parent_stmt & lib.LY_STMT_NODE_MASK):
            return None
        try:
            return SNode.new(self.context, self.cdata.parent)
        except LibyangError:
            return None


# -------------------------------------------------------------------------------------
class _EnumBit:
    __slots__ = ("context", "cdata", "__dict__")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type "struct lys_type_bit" or "struct lys_type_enum"

    def position(self) -> int:
        return self.cdata.position

    def value(self) -> int:
        return self.cdata.value

    def name(self) -> str:
        return c2str(self.cdata.name)

    def description(self) -> str:
        return c2str(self.cdata.dsc)

    def deprecated(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_OBSLT)

    def status(self) -> str:
        if self.cdata.flags & lib.LYS_STATUS_OBSLT:
            return "obsolete"
        if self.cdata.flags & lib.LYS_STATUS_DEPRC:
            return "deprecated"
        return "current"

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, self)

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class Enum(_EnumBit):
    pass


# -------------------------------------------------------------------------------------
class Bit(_EnumBit):
    pass


# -------------------------------------------------------------------------------------
class Pattern:
    __slots__ = ("context", "cdata", "cdata_parsed")

    def __init__(self, context: "libyang.Context", cdata, cdata_parsed=None):
        self.context = context
        self.cdata = cdata  # C type: "struct lysc_pattern *"
        self.cdata_parsed = cdata_parsed  # C type: "struct lysp_restr *"

    def expression(self) -> str:
        if self.cdata is None and self.cdata_parsed:
            return c2str(self.cdata_parsed.arg.str + 1)
        return c2str(self.cdata.expr)

    def inverted(self) -> bool:
        if self.cdata is None and self.cdata_parsed:
            return self.cdata_parsed.arg.str[0] == b"\x15"
        return self.cdata.inverted

    def error_message(self) -> Optional[str]:
        if self.cdata is None and self.cdata_parsed:
            return c2str(self.cdata_parsed.emsg)
        return c2str(self.cdata.emsg) if self.cdata.emsg != ffi.NULL else None


# -------------------------------------------------------------------------------------
class Type:
    __slots__ = ("context", "cdata", "cdata_parsed", "__dict__")

    UNKNOWN = lib.LY_TYPE_UNKNOWN
    BINARY = lib.LY_TYPE_BINARY
    UINT8 = lib.LY_TYPE_UINT8
    UINT16 = lib.LY_TYPE_UINT16
    UINT32 = lib.LY_TYPE_UINT32
    UINT64 = lib.LY_TYPE_UINT64
    STRING = lib.LY_TYPE_STRING
    BITS = lib.LY_TYPE_BITS
    BOOL = lib.LY_TYPE_BOOL
    DEC64 = lib.LY_TYPE_DEC64
    EMPTY = lib.LY_TYPE_EMPTY
    ENUM = lib.LY_TYPE_ENUM
    IDENT = lib.LY_TYPE_IDENT
    INST = lib.LY_TYPE_INST
    LEAFREF = lib.LY_TYPE_LEAFREF
    UNION = lib.LY_TYPE_UNION
    INT8 = lib.LY_TYPE_INT8
    INT16 = lib.LY_TYPE_INT16
    INT32 = lib.LY_TYPE_INT32
    INT64 = lib.LY_TYPE_INT64

    BASENAMES = {
        UNKNOWN: "unknown",
        BINARY: "binary",
        UINT8: "uint8",
        UINT16: "uint16",
        UINT32: "uint32",
        UINT64: "uint64",
        STRING: "string",
        BITS: "bits",
        BOOL: "boolean",
        DEC64: "decimal64",
        EMPTY: "empty",
        ENUM: "enumeration",
        IDENT: "identityref",
        INST: "instance-id",
        LEAFREF: "leafref",
        UNION: "union",
        INT8: "int8",
        INT16: "int16",
        INT32: "int32",
        INT64: "int64",
    }

    def __init__(self, context: "libyang.Context", cdata, cdata_parsed):
        self.context = context
        self.cdata = cdata  # C type: "struct lysc_type*"
        self.cdata_parsed = cdata_parsed  # C type: "struct lysp_type*"

    def get_bases(self) -> Iterator["Type"]:
        if self.cdata.basetype == lib.LY_TYPE_LEAFREF:
            yield from self.leafref_type().get_bases()
        elif self.cdata.basetype == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.get_bases()
        else:  # builtin type
            yield self

    def name(self) -> str:
        if self.cdata_parsed is not None and self.cdata_parsed.name:
            return c2str(self.cdata_parsed.name)
        return self.basename()

    def description(self) -> Optional[str]:
        typedef = self.typedef()
        if typedef:
            return typedef.description()
        return None

    def base(self) -> int:
        return self.cdata.basetype

    def bases(self) -> Iterator[int]:
        for b in self.get_bases():
            yield b.base()

    def basename(self) -> str:
        return self.BASENAMES.get(self.cdata.basetype, "unknown")

    def basenames(self) -> Iterator[str]:
        for b in self.get_bases():
            yield b.basename()

    def leafref_type(self) -> Optional["Type"]:
        if self.cdata.basetype != self.LEAFREF:
            return None
        lr = ffi.cast("struct lysc_type_leafref *", self.cdata)
        return Type(self.context, lr.realtype, None)

    def leafref_path(self) -> Optional["str"]:
        if self.cdata.basetype != self.LEAFREF:
            return None
        lr = ffi.cast("struct lysc_type_leafref *", self.cdata)
        return c2str(lib.lyxp_get_expr(lr.path))

    def typedef(self) -> "Typedef":
        if ":" in self.name():
            module_prefix, type_name = self.name().split(":")
            import_module = self.module().get_module_from_prefix(module_prefix)
            if import_module:
                return import_module.get_typedef(type_name)
        return None

    def union_types(self, with_typedefs: bool = False) -> Iterator["Type"]:
        if self.cdata.basetype != self.UNION:
            return

        typedef = self.typedef()
        t = ffi.cast("struct lysc_type_union *", self.cdata)
        if self.cdata_parsed and self.cdata_parsed.types != ffi.NULL:
            for union_type, union_type_parsed in zip(
                ly_array_iter(t.types), ly_array_iter(self.cdata_parsed.types)
            ):
                yield Type(self.context, union_type, union_type_parsed)
        elif (
            with_typedefs
            and typedef
            and typedef.cdata
            and typedef.cdata.type.types != ffi.NULL
        ):
            for union_type, union_type_parsed in zip(
                ly_array_iter(t.types), ly_array_iter(typedef.cdata.type.types)
            ):
                yield Type(self.context, union_type, union_type_parsed)
        else:
            for union_type in ly_array_iter(t.types):
                yield Type(self.context, union_type, None)

    def enums(self) -> Iterator[Enum]:
        if self.cdata.basetype != self.ENUM:
            return
        t = ffi.cast("struct lysc_type_enum *", self.cdata)
        for enum in ly_array_iter(t.enums):
            yield Enum(self.context, enum)

    def all_enums(self) -> Iterator[Enum]:
        for b in self.get_bases():
            yield from b.enums()

    def bits(self) -> Iterator[Bit]:
        if self.cdata.basetype != self.BITS:
            return
        t = ffi.cast("struct lysc_type_bits *", self.cdata)
        for bit in ly_array_iter(t.bits):
            yield Enum(self.context, bit)

    def all_bits(self) -> Iterator[Bit]:
        for b in self.get_bases():
            yield from b.bits()

    NUM_TYPES = frozenset((INT8, INT16, INT32, INT64, UINT8, UINT16, UINT32, UINT64))

    def range(self) -> Optional[str]:
        if not self.cdata_parsed:
            return None
        if (
            self.cdata.basetype in self.NUM_TYPES or self.cdata.basetype == self.DEC64
        ) and self.cdata_parsed.range != ffi.NULL:
            return c2str(self.cdata_parsed.range.arg.str)
        return None

    def all_ranges(self) -> Iterator[str]:
        if self.cdata.basetype == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_ranges()
        else:
            rng = self.range()
            if rng is not None:
                yield rng

    def fraction_digits(self) -> Optional[int]:
        if not self.cdata_parsed:
            return None
        if self.cdata.basetype != self.DEC64:
            return None
        return self.cdata_parsed.fraction_digits

    def all_fraction_digits(self) -> Iterator[int]:
        if self.cdata.basetype == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_fraction_digits()
        else:
            fd = self.fraction_digits()
            if fd is not None:
                yield fd

    STR_TYPES = frozenset((STRING, BINARY, ENUM, IDENT, BITS))

    def length(self) -> Optional[str]:
        if not self.cdata_parsed:
            return None
        if (
            self.cdata.basetype in (self.STRING, self.BINARY)
        ) and self.cdata_parsed.length != ffi.NULL:
            return c2str(self.cdata_parsed.length.arg.str)
        return None

    def all_lengths(self) -> Iterator[str]:
        if self.cdata.basetype == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_lengths()
        else:
            length = self.length()
            if length is not None:
                yield length

    def patterns(self) -> Iterator[Tuple[str, bool]]:
        if not self.cdata_parsed or self.cdata.basetype != self.STRING:
            return
        if self.cdata_parsed.patterns == ffi.NULL:
            return
        for p in ly_array_iter(self.cdata_parsed.patterns):
            if not p:
                continue
            # in case of pattern restriction, the first byte has a special meaning:
            # 0x06 (ACK) for regular match and 0x15 (NACK) for invert-match
            invert_match = p.arg.str[0] == b"\x15"
            # yield tuples like:
            #     ('[a-zA-Z_][a-zA-Z0-9\-_.]*', False)
            #     ('[xX][mM][lL].*', True)
            yield c2str(p.arg.str + 1), invert_match

    def all_patterns(self) -> Iterator[Tuple[str, bool]]:
        if self.cdata.basetype == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_patterns()
        else:
            yield from self.patterns()

    def pattern_details(self) -> Iterator[Pattern]:
        if self.cdata.basetype != self.STRING:
            return
        t = ffi.cast("struct lysc_type_str *", self.cdata)
        if t.patterns == ffi.NULL:
            return
        for p in ly_array_iter(t.patterns):
            if not p:
                continue
            yield Pattern(self.context, p)

    def all_pattern_details(self) -> Iterator[Pattern]:
        if self.cdata.basetype == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_pattern_details()
        else:
            yield from self.pattern_details()

    def require_instance(self) -> Optional[bool]:
        if self.cdata.basetype != self.LEAFREF:
            return None
        t = ffi.cast("struct lysc_type_leafref *", self.cdata)
        return bool(t.require_instance)

    def module(self) -> Module:
        if not self.cdata_parsed:
            return None
        return Module(self.context, self.cdata_parsed.pmod.mod)

    def extensions(self) -> Iterator[ExtensionCompiled]:
        for extension in ly_array_iter(self.cdata.exts):
            yield ExtensionCompiled(self.context, extension)

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional[ExtensionCompiled]:
        for ext in self.extensions():
            if ext.name() != name:
                continue
            if prefix is not None and ext.module().name() != prefix:
                continue
            if arg_value is not None and ext.argument() != arg_value:
                continue
            return ext
        return None

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()

    def parsed(self) -> Optional["PType"]:
        if self.cdata_parsed is None or self.cdata_parsed == ffi.NULL:
            return None
        return PType(self.context, self.cdata_parsed, self.module())


# -------------------------------------------------------------------------------------
class Typedef:
    __slots__ = ("context", "cdata", "__dict__")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lysp_tpdf *"

    def name(self) -> str:
        return c2str(self.cdata.name)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def units(self) -> Optional[str]:
        return c2str(self.cdata.units)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def extensions(self) -> Iterator[ExtensionCompiled]:
        ext = ffi.cast("struct lysc_ext_instance *", self.cdata.exts)
        if ext == ffi.NULL:
            return
        for extension in ly_array_iter(ext):
            yield ExtensionCompiled(self.context, extension)

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional[ExtensionCompiled]:
        for ext in self.extensions():
            if ext.name() != name:
                continue
            if prefix is not None and ext.module().name() != prefix:
                continue
            if arg_value is not None and ext.argument() != arg_value:
                continue
            return ext
        return None

    def deprecated(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_OBSLT)

    def module(self) -> Module:
        return Module(self.context, self.cdata.module)

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class Feature:
    __slots__ = ("context", "cdata", "__dict__")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lysp_feature *"

    def name(self) -> str:
        return c2str(self.cdata.name)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def state(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_FENABLED)

    def deprecated(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_OBSLT)

    def if_features(self) -> Iterator["IfFeatureExpr"]:
        arr_length = ffi.cast("uint64_t *", self.cdata.iffeatures)[-1]
        for i in range(arr_length):
            yield IfFeatureExpr(self.context, self.cdata.iffeatures[i])

    def test_all_if_features(self) -> Iterator["IfFeatureExpr"]:
        for cdata_lysc_iffeature in ly_array_iter(self.cdata.iffeatures_c):
            for cdata_feature in ly_array_iter(cdata_lysc_iffeature.features):
                yield Feature(self.context, cdata_feature)

    def module(self) -> Module:
        return Module(self.context, self.cdata.module)

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class IfFeatureExpr:
    __slots__ = ("context", "cdata", "module_features", "compiled", "__dict__")

    def __init__(self, context: "libyang.Context", cdata, module_features=None):
        """
        if module_features is not None, it means we are using a parsed IfFeatureExpr
        """
        self.context = context
        # Can be "struct lysc_iffeature *" if comes from module feature
        # Can be "struct lysp_qname *" if comes from lysp_node
        self.cdata = cdata
        self.module_features = module_features
        self.compiled = not module_features

    def _get_operator(self, position: int) -> int:
        # the ->exp field is a 2bit array of operator values stored under a uint8_t C
        # array.
        mask = 0x3  # 2bits mask
        shift = 2 * (position % 4)
        item = self.cdata.expr[position // 4]
        result = item & (mask << shift)
        return result >> shift

    def _get_operands_parsed(self):
        qname = ffi.string(self.cdata.str).decode()
        tokens = qname.split()
        operators = []
        features = []
        operators_map = {
            "or": lib.LYS_IFF_OR,
            "and": lib.LYS_IFF_AND,
            "not": lib.LYS_IFF_NOT,
            "f": lib.LYS_IFF_F,
        }

        def get_feature(name):
            for feature in self.module_features:
                if feature.name() == name:
                    return feature.cdata
            raise LibyangError("No feature %s in module" % name)

        def parse_iffeature(tokens):
            def oper2(op):
                op_index = tokens.index(op)
                operators.append(operators_map[op])
                left, right = tokens[:op_index], tokens[op_index + 1 :]
                parse_iffeature(left)
                parse_iffeature(right)

            def oper1(op):
                op_index = tokens.index(op)
                feature_name = tokens[op_index + 1]
                operators.append(operators_map[op])
                operators.append(operators_map["f"])
                features.append(get_feature(feature_name))

            oper_map = {"or": oper2, "and": oper2, "not": oper1}
            for op, fun in oper_map.items():
                with suppress(ValueError):
                    fun(op)
                    return

            # Token is a feature
            operators.append(operators_map["f"])
            features.append(get_feature(tokens[0]))

        parse_iffeature(tokens)

        return operators, features

    def _operands(self) -> Iterator[Union["IfFeature", type]]:
        if self.compiled:

            def get_operator(op_index):
                return self._get_operator(op_index)

            def get_feature(ft_index):
                return self.cdata.features[ft_index]

        else:
            operators, features = self._get_operands_parsed()

            def get_operator(op_index):
                return operators[op_index]

            def get_feature(ft_index):
                return features[ft_index]

        op_index = 0
        ft_index = 0
        expected = 1
        while expected > 0:
            operator = get_operator(op_index)
            op_index += 1
            if operator == lib.LYS_IFF_F:
                yield IfFeature(self.context, get_feature(ft_index))
                ft_index += 1
                expected -= 1
            elif operator == lib.LYS_IFF_NOT:
                yield IfNotFeature
            elif operator == lib.LYS_IFF_AND:
                yield IfAndFeatures
                expected += 1
            elif operator == lib.LYS_IFF_OR:
                yield IfOrFeatures
                expected += 1

    def tree(self) -> "IfFeatureExprTree":
        def _tree(operands):
            op = next(operands)
            if op is IfNotFeature:
                return op(self.context, _tree(operands))
            if op in (IfAndFeatures, IfOrFeatures):
                return op(self.context, _tree(operands), _tree(operands))
            return op

        return _tree(self._operands())

    def dump(self) -> str:
        return self.tree().dump()

    def __str__(self):
        return str(self.tree()).strip("()")


# -------------------------------------------------------------------------------------
class IfFeatureExprTree:
    def dump(self, indent: int = 0) -> str:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


# -------------------------------------------------------------------------------------
class IfFeature(IfFeatureExprTree):
    __slots__ = ("context", "cdata")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_feature *"

    def feature(self) -> Feature:
        return Feature(self.context, self.cdata)

    def state(self) -> bool:
        return self.feature().state()

    def dump(self, indent: int = 0) -> str:
        feat = self.feature()
        return "%s%s [%s]\n" % (" " * indent, feat.name(), feat.description())

    def __str__(self):
        return self.feature().name()


# -------------------------------------------------------------------------------------
class IfNotFeature(IfFeatureExprTree):
    __slots__ = ("context", "child")

    def __init__(self, context: "libyang.Context", child: IfFeatureExprTree):
        self.context = context
        self.child = child

    def state(self) -> bool:
        return not self.child.state()

    def dump(self, indent: int = 0) -> str:
        return " " * indent + "NOT\n" + self.child.dump(indent + 1)

    def __str__(self):
        return "NOT %s" % self.child


# -------------------------------------------------------------------------------------
class IfAndFeatures(IfFeatureExprTree):
    __slots__ = ("context", "a", "b")

    def __init__(
        self, context: "libyang.Context", a: IfFeatureExprTree, b: IfFeatureExprTree
    ):
        self.context = context
        self.a = a
        self.b = b

    def state(self) -> bool:
        return self.a.state() and self.b.state()

    def dump(self, indent: int = 0) -> str:
        s = " " * indent + "AND\n"
        s += self.a.dump(indent + 1)
        s += self.b.dump(indent + 1)
        return s

    def __str__(self):
        return "%s AND %s" % (self.a, self.b)


# -------------------------------------------------------------------------------------
class IfOrFeatures(IfFeatureExprTree):
    __slots__ = ("context", "a", "b")

    def __init__(
        self, context: "libyang.Context", a: IfFeatureExprTree, b: IfFeatureExprTree
    ):
        self.context = context
        self.a = a
        self.b = b

    def state(self) -> bool:
        return self.a.state() or self.b.state()

    def dump(self, indent: int = 0) -> str:
        s = " " * indent + "OR\n"
        s += self.a.dump(indent + 1)
        s += self.b.dump(indent + 1)
        return s

    def __str__(self):
        return "(%s OR %s)" % (self.a, self.b)


# -------------------------------------------------------------------------------------
class Must:
    __slots__ = ("context", "cdata", "cdata_parsed")

    def __init__(self, context: "libyang.Context", cdata, cdata_parsed=None):
        self.context = context
        self.cdata = cdata  # C type: "struct lysc_must *"
        self.cdata_parsed = cdata_parsed  # C type: "struct lysp_must *"

    def condition(self) -> str:
        if self.cdata is None and self.cdata_parsed:
            return c2str(self.cdata_parsed.arg.str + 1)
        return c2str(lib.lyxp_get_expr(self.cdata.cond))

    def error_message(self) -> Optional[str]:
        if self.cdata is None and self.cdata_parsed:
            return c2str(self.cdata_parsed.emsg)
        return c2str(self.cdata.emsg) if self.cdata.emsg != ffi.NULL else None


# -------------------------------------------------------------------------------------
class SNode:
    __slots__ = ("context", "cdata", "cdata_parsed", "__dict__")

    CONTAINER = lib.LYS_CONTAINER
    CHOICE = lib.LYS_CHOICE
    CASE = lib.LYS_CASE
    LEAF = lib.LYS_LEAF
    LEAFLIST = lib.LYS_LEAFLIST
    LIST = lib.LYS_LIST
    RPC = lib.LYS_RPC
    ACTION = lib.LYS_ACTION
    INPUT = lib.LYS_INPUT
    OUTPUT = lib.LYS_OUTPUT
    NOTIF = lib.LYS_NOTIF
    ANYXML = lib.LYS_ANYXML
    ANYDATA = lib.LYS_ANYDATA
    KEYWORDS = {
        CONTAINER: "container",
        LEAF: "leaf",
        LEAFLIST: "leaf-list",
        LIST: "list",
        RPC: "rpc",
        ACTION: "action",
        INPUT: "input",
        OUTPUT: "output",
        NOTIF: "notification",
        ANYXML: "anyxml",
        ANYDATA: "anydata",
    }

    PATH_LOG = lib.LYSC_PATH_LOG
    PATH_DATA = lib.LYSC_PATH_DATA
    PATH_DATA_PATTERN = lib.LYSC_PATH_DATA_PATTERN

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lysc_node *"
        self.cdata_parsed = ffi.cast("struct lysp_node *", self.cdata.priv)

    def nodetype(self) -> int:
        return self.cdata.nodetype

    def keyword(self) -> str:
        return self.KEYWORDS.get(self.cdata.nodetype, "???")

    def name(self) -> str:
        return c2str(self.cdata.name)

    def fullname(self) -> str:
        return "%s:%s" % (self.module().name(), self.name())

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def config_set(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_SET_CONFIG)

    def config_false(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_CONFIG_R)

    def mandatory(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_MAND_TRUE)

    def deprecated(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_OBSLT)

    def status(self) -> str:
        if self.cdata.flags & lib.LYS_STATUS_OBSLT:
            return "obsolete"
        if self.cdata.flags & lib.LYS_STATUS_DEPRC:
            return "deprecated"
        return "current"

    def module(self) -> Module:
        return Module(self.context, self.cdata.module)

    def schema_path(self, path_type: int = PATH_LOG) -> str:
        try:
            s = lib.lysc_path(self.cdata, path_type, ffi.NULL, 0)
            return c2str(s)
        finally:
            lib.free(s)

    def data_path(self, key_placeholder: str = "'%s'") -> str:
        val = self.schema_path(self.PATH_DATA_PATTERN)

        if key_placeholder != "'%s'":
            val = val.replace("'%s'", key_placeholder)
        return val

    def extensions(self) -> Iterator[ExtensionCompiled]:
        ext = ffi.cast("struct lysc_ext_instance *", self.cdata.exts)
        if ext == ffi.NULL:
            return
        for extension in ly_array_iter(ext):
            yield ExtensionCompiled(self.context, extension)

    def must_conditions(self) -> Iterator[str]:
        for must in self.musts():
            yield must.condition()

    def musts(self) -> Iterator[Must]:
        mc = lib.lysc_node_musts(self.cdata)
        if mc == ffi.NULL:
            return
        for m in ly_array_iter(mc):
            if not m:
                continue
            yield Must(self.context, m)

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional[ExtensionCompiled]:
        for ext in self.extensions():
            if ext.name() != name:
                continue
            if prefix is not None and ext.module().name() != prefix:
                continue
            if arg_value is not None and ext.argument() != arg_value:
                continue
            return ext
        return None

    def if_features(self) -> Iterator[IfFeatureExpr]:
        iff = ffi.cast("struct  lysp_qname *", self.cdata_parsed.iffeatures)
        module_features = self.module().features()
        for if_feature in ly_array_iter(iff):
            yield IfFeatureExpr(self.context, if_feature, list(module_features))

    def parent(self) -> Optional["SNode"]:
        parent_p = self.cdata.parent
        while parent_p and parent_p.nodetype not in SNode.NODETYPE_CLASS:
            parent_p = parent_p.parent
        if parent_p:
            return SNode.new(self.context, parent_p)
        return None

    def when_conditions(self):
        wh = ffi.new("struct lysc_when **")
        wh = lib.lysc_node_when(self.cdata)
        if wh == ffi.NULL:
            return
        for cond in ly_array_iter(wh):
            yield c2str(lib.lyxp_get_expr(cond.cond))

    def parsed(self) -> Optional["PNode"]:
        if self.cdata_parsed is None or self.cdata_parsed == ffi.NULL:
            return None
        return PNode.new(self.context, self.cdata_parsed, self.module())

    def iter_tree(self, full: bool = False) -> Iterator["SNode"]:
        """
        Do a DFS walk of the schema node.

        :arg full:
            Also walk in actions and notifications.
        """
        n = next_n = self.cdata
        while n != ffi.NULL:
            yield self.new(self.context, n)

            if full:
                act = lib.lysc_node_actions(n)
                if act != ffi.NULL:
                    yield from self.new(self.context, act).iter_tree()
                notif = lib.lysc_node_notifs(n)
                if notif != ffi.NULL:
                    yield from self.new(self.context, notif).iter_tree()

            next_n = lib.lysc_node_child(n)
            if next_n == ffi.NULL:
                if n == self.cdata:
                    break
                next_n = n.next
            while next_n == ffi.NULL:
                n = n.parent
                if n.parent == self.cdata.parent:
                    break
                next_n = n.next
            n = next_n

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()

    NODETYPE_CLASS = {}

    @staticmethod
    def register(nodetype):
        def _decorator(nodeclass):
            SNode.NODETYPE_CLASS[nodetype] = nodeclass
            return nodeclass

        return _decorator

    @staticmethod
    def new(context: "libyang.Context", cdata) -> "SNode":
        cdata = ffi.cast("struct lysc_node *", cdata)
        nodecls = SNode.NODETYPE_CLASS.get(cdata.nodetype, None)
        if nodecls is None:
            raise TypeError("node type %s not implemented" % cdata.nodetype)
        return nodecls(context, cdata)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.LEAF)
class SLeaf(SNode):
    __slots__ = ("cdata_leaf", "cdata_leaf_parsed")

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_leaf = ffi.cast("struct lysc_node_leaf *", cdata)
        self.cdata_leaf_parsed = ffi.cast("struct lysp_node_leaf *", self.cdata_parsed)

    def default(self) -> Union[None, bool, int, str, float]:
        if not self.cdata_leaf.dflt:
            return None
        val = lib.lyd_value_get_canonical(self.context.cdata, self.cdata_leaf.dflt)
        if not val:
            return None
        val = c2str(val)
        val_type = Type(self.context, self.cdata_leaf.dflt.realtype, None)
        if val_type.base() == Type.BOOL:
            return val == "true"
        if val_type.base() in Type.NUM_TYPES:
            return int(val)
        if val_type.base() == Type.DEC64:
            return float(val)
        return val

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaf.units)

    def type(self) -> Type:
        return Type(self.context, self.cdata_leaf.type, self.cdata_leaf_parsed.type)

    def is_key(self) -> bool:
        if self.cdata_leaf.flags & lib.LYS_KEY:
            return True
        return False

    def __str__(self):
        return "%s %s" % (self.name(), self.type().name())


# -------------------------------------------------------------------------------------
@SNode.register(SNode.LEAFLIST)
class SLeafList(SNode):
    __slots__ = ("cdata_leaflist", "cdata_leaflist_parsed")

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_leaflist = ffi.cast("struct lysc_node_leaflist *", cdata)
        self.cdata_leaflist_parsed = ffi.cast(
            "struct lysp_node_leaflist *", self.cdata_parsed
        )

    def ordered(self) -> bool:
        return bool(self.cdata_parsed.flags & lib.LYS_ORDBY_USER)

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaflist.units)

    def type(self) -> Type:
        return Type(
            self.context, self.cdata_leaflist.type, self.cdata_leaflist_parsed.type
        )

    def defaults(self) -> Iterator[Union[None, bool, int, str, float]]:
        if self.cdata_leaflist.dflts == ffi.NULL:
            return
        for dflt in ly_array_iter(self.cdata_leaflist.dflts):
            val = lib.lyd_value_get_canonical(self.context.cdata, dflt)
            if not val:
                yield None
            val = c2str(val)
            val_type = Type(self.context, dflt.realtype, None)
            if val_type.base() == Type.BOOL:
                yield val == "true"
            elif val_type.base() in Type.NUM_TYPES:
                yield int(val)
            elif val_type.base() == Type.DEC64:
                yield float(val)
            else:
                yield val

    def max_elements(self) -> Optional[int]:
        return (
            self.cdata_leaflist.max
            if self.cdata_leaflist.max != (2**32 - 1)
            else None
        )

    def min_elements(self) -> int:
        return self.cdata_leaflist.min

    def __str__(self):
        return "%s %s" % (self.name(), self.type().name())


# -------------------------------------------------------------------------------------
@SNode.register(SNode.CONTAINER)
class SContainer(SNode):
    __slots__ = ("cdata_container", "cdata_container_parsed")

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_container = ffi.cast("struct lysc_node_container *", cdata)
        self.cdata_container_parsed = ffi.cast(
            "struct lysp_node_container *", self.cdata_parsed
        )

    def presence(self) -> Optional[str]:
        if not self.cdata_container.flags & lib.LYS_PRESENCE:
            return None

        return c2str(self.cdata_container_parsed.presence)

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(
        self, types: Optional[Tuple[int, ...]] = None, with_choice: bool = False
    ) -> Iterator[SNode]:
        return iter_children(
            self.context, self.cdata, types=types, with_choice=with_choice
        )


# -------------------------------------------------------------------------------------
@SNode.register(SNode.CHOICE)
class SChoice(SNode):
    __slots__ = ("cdata_choice",)

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_choice = ffi.cast("struct lysc_node_choice *", cdata)

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(
        self, types: Optional[Tuple[int, ...]] = None, with_case: bool = False
    ) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, types=types, with_case=with_case)

    def default(self) -> Optional[SNode]:
        if self.cdata_choice.dflt == ffi.NULL:
            return None
        return SNode.new(self.context, self.cdata_choice.dflt)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.CASE)
class SCase(SNode):
    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(
        self, types: Optional[Tuple[int, ...]] = None, with_choice: bool = False
    ) -> Iterator[SNode]:
        return iter_children(
            self.context, self.cdata, types=types, with_choice=with_choice
        )


# -------------------------------------------------------------------------------------
@SNode.register(SNode.LIST)
class SList(SNode):
    __slots__ = ("cdata_list", "cdata_list_parsed")

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_list = ffi.cast("struct lysc_node_list *", cdata)
        self.cdata_list_parsed = ffi.cast("struct lysp_node_list *", self.cdata_parsed)

    def ordered(self) -> bool:
        return bool(self.cdata_parsed.flags & lib.LYS_ORDBY_USER)

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(
        self,
        skip_keys: bool = False,
        types: Optional[Tuple[int, ...]] = None,
        with_choice: bool = False,
    ) -> Iterator[SNode]:
        return iter_children(
            self.context,
            self.cdata,
            skip_keys=skip_keys,
            types=types,
            with_choice=with_choice,
        )

    def keys(self) -> Iterator[SNode]:
        node = lib.lysc_node_child(self.cdata)
        while node:
            if node.flags & lib.LYS_KEY:
                yield SLeaf(self.context, node)
            node = node.next

    def uniques(self) -> Iterator[List[SNode]]:
        for unique in ly_array_iter(self.cdata_list.uniques):
            nodes = []
            for node in ly_array_iter(unique):
                nodes.append(SNode.new(self.context, node))
            yield nodes

    def max_elements(self) -> Optional[int]:
        return self.cdata_list.max if self.cdata_list.max != (2**32 - 1) else None

    def min_elements(self) -> int:
        return self.cdata_list.min

    def __str__(self):
        return "%s [%s]" % (self.name(), ", ".join(k.name() for k in self.keys()))


# -------------------------------------------------------------------------------------
@SNode.register(SNode.INPUT)
@SNode.register(SNode.OUTPUT)
class SRpcInOut(SNode):
    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, types=types)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.RPC)
@SNode.register(SNode.ACTION)
class SRpc(SNode):
    def input(self) -> Optional[SRpcInOut]:
        node = lib.lysc_node_child(self.cdata)
        while True:
            if not node:
                break
            if node.nodetype == self.INPUT:
                return SNode.new(self.context, node)
            node = node.next
        return None

    def output(self) -> Optional[SRpcInOut]:
        node = lib.lysc_node_child(self.cdata)
        while True:
            if not node:
                break
            if node.nodetype == self.OUTPUT:
                return SNode.new(self.context, node)
            node = node.next
        return None

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator[SNode]:
        yield from iter_children(self.context, self.cdata, types=types)
        # With libyang2, you can get only input or output
        # To keep behavior, we iter 2 times witt output options
        yield from iter_children(self.context, self.cdata, types=types, output=True)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.NOTIF)
class SNotif(SNode):
    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, types=types)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.ANYXML)
class SAnyxml(SNode):
    pass


# -------------------------------------------------------------------------------------
@SNode.register(SNode.ANYDATA)
class SAnydata(SNode):
    pass


# -------------------------------------------------------------------------------------
def iter_children_options(
    with_choice: bool = False,
    no_choice: bool = False,
    with_case: bool = False,
    into_non_presence_container: bool = False,
    output: bool = False,
    with_schema_mount: bool = False,
) -> int:
    options = 0
    if with_choice:
        options |= lib.LYS_GETNEXT_WITHCHOICE
    if no_choice:
        options |= lib.LYS_GETNEXT_NOCHOICE
    if with_case:
        options |= lib.LYS_GETNEXT_WITHCASE
    if into_non_presence_container:
        options |= lib.LYS_GETNEXT_INTONPCONT
    if output:
        options |= lib.LYS_GETNEXT_OUTPUT
    if with_schema_mount:
        options |= lib.LYS_GETNEXT_WITHSCHEMAMOUNT
    return options


# -------------------------------------------------------------------------------------
def iter_children(
    context: "libyang.Context",
    parent,  # C type: Union["struct lys_module *", "struct lys_node *"]
    skip_keys: bool = False,
    types: Optional[Tuple[int, ...]] = None,
    with_choice: bool = False,
    no_choice: bool = False,
    with_case: bool = False,
    into_non_presence_container: bool = False,
    output: bool = False,
    with_schema_mount: bool = False,
) -> Iterator[SNode]:
    if types is None:
        types = (
            lib.LYS_ACTION,
            lib.LYS_CONTAINER,
            lib.LYS_LIST,
            lib.LYS_RPC,
            lib.LYS_LEAF,
            lib.LYS_LEAFLIST,
            lib.LYS_NOTIF,
            lib.LYS_CHOICE,
            lib.LYS_CASE,
        )

    def _skip(node) -> bool:
        if node.nodetype not in types:
            return True
        if not skip_keys:
            return False
        if node.nodetype != lib.LYS_LEAF:
            return False
        leaf = ffi.cast("struct lysc_node_leaf *", node)
        if leaf.flags & lib.LYS_KEY:
            return True
        return False

    if ffi.typeof(parent) == ffi.typeof("struct lys_module *"):
        if parent.compiled == ffi.NULL:
            return
        module = parent.compiled
        parent = ffi.NULL
    else:
        module = ffi.NULL

    options = iter_children_options(
        with_choice=with_choice,
        no_choice=no_choice,
        with_case=with_case,
        into_non_presence_container=into_non_presence_container,
        output=output,
        with_schema_mount=with_schema_mount,
    )
    child = lib.lys_getnext(ffi.NULL, parent, module, options)
    while child:
        if not _skip(child):
            yield SNode.new(context, child)
        child = lib.lys_getnext(child, parent, module, options)


# -------------------------------------------------------------------------------------
# compat
Container = SContainer
Leaf = SLeaf
LeafList = SLeafList
List = SList
Node = SNode
Rpc = SRpc
RpcInOut = SRpcInOut
Anyxml = SAnyxml


# -------------------------------------------------------------------------------------
class PEnum:
    __slots__ = ("context", "cdata", "module")

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        self.context = context
        self.cdata = cdata  # C type of "struct lysp_type_enum *"
        self.module = module

    def name(self) -> str:
        return c2str(self.cdata.name)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def value(self) -> int:
        return self.cdata.value

    def if_features(self) -> Iterator[IfFeatureExpr]:
        for f in ly_array_iter(self.cdata.iffeatures):
            yield IfFeatureExpr(self.context, f, list(self.module.features()))

    def extensions(self) -> Iterator["ExtensionParsed"]:
        for ext in ly_array_iter(self.cdata.exts):
            yield ExtensionParsed(self.context, ext, self.module)


# -------------------------------------------------------------------------------------
class PType:
    __slots__ = ("context", "cdata", "module")

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        self.context = context
        self.cdata = cdata  # C type of "struct lysp_type *"
        self.module = module

    def name(self) -> str:
        return c2str(self.cdata.name)

    def range(self) -> Optional[str]:
        if self.cdata.range == ffi.NULL:
            return None
        return c2str(self.cdata.range.arg.str)

    def length(self) -> Optional[str]:
        if self.cdata.length == ffi.NULL:
            return None
        return c2str(self.cdata.length.arg.str)

    def patterns(self) -> Iterator[Pattern]:
        for p in ly_array_iter(self.cdata.patterns):
            yield Pattern(self.context, None, p)

    def enums(self) -> Iterator[PEnum]:
        for e in ly_array_iter(self.cdata.enums):
            yield PEnum(self.context, e, self.module)

    def bits(self) -> Iterator[PEnum]:
        for b in ly_array_iter(self.cdata.bits):
            yield PEnum(self.context, b, self.module)

    def path(self) -> Optional[str]:
        if self.cdata.path == ffi.NULL:
            return None
        return c2str(lib.lyxp_get_expr(self.cdata.path))

    def bases(self) -> Iterator[str]:
        for b in ly_array_iter(self.cdata.bases):
            yield c2str(b)

    def types(self) -> Iterator["PType"]:
        for t in ly_array_iter(self.cdata.types):
            yield PType(self.context, t, self.module)

    def extensions(self) -> Iterator["ExtensionParsed"]:
        for ext in ly_array_iter(self.cdata.exts):
            yield ExtensionParsed(self.context, ext, self.module)

    def pmod(self) -> Optional[Module]:
        if self.cdata.pmod == ffi.NULL:
            return None
        return Module(self.context, self.cdata.pmod.mod)

    def compiled(self) -> Optional[Type]:
        if self.cdata.compiled == ffi.NULL:
            return None
        return Type(self.context, self.cdata.compiled, self.cdata)

    def fraction_digits(self) -> int:
        return self.cdata.fraction_digits

    def require_instance(self) -> bool:
        return self.cdata.require_instance


# -------------------------------------------------------------------------------------
class PRefine:
    __slots__ = ("context", "cdata", "module")

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        self.context = context
        self.cdata = cdata  # C type of "struct lysp_refine *"
        self.module = module

    def nodeid(self) -> str:
        return c2str(self.cdata.nodeid)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def if_features(self) -> Iterator[IfFeatureExpr]:
        for f in ly_array_iter(self.cdata.iffeatures):
            yield IfFeatureExpr(self.context, f, list(self.module.features()))

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata.musts):
            yield Must(self.context, None, m)

    def presence(self) -> Optional[str]:
        return c2str(self.cdata.presence)

    def defaults(self) -> Iterator[str]:
        for d in ly_array_iter(self.cdata.dflts):
            yield c2str(d.str)

    def min_elements(self) -> int:
        return self.cdata.min

    def max_elements(self) -> Optional[int]:
        return self.cdata.max if self.cdata.max != 0 else None

    def extensions(self) -> Iterator["ExtensionParsed"]:
        for ext in ly_array_iter(self.cdata.exts):
            yield ExtensionParsed(self.context, ext, self.module)


# -------------------------------------------------------------------------------------
class PNode:
    CONTAINER = lib.LYS_CONTAINER
    CHOICE = lib.LYS_CHOICE
    CASE = lib.LYS_CASE
    LEAF = lib.LYS_LEAF
    LEAFLIST = lib.LYS_LEAFLIST
    LIST = lib.LYS_LIST
    RPC = lib.LYS_RPC
    ACTION = lib.LYS_ACTION
    INPUT = lib.LYS_INPUT
    OUTPUT = lib.LYS_OUTPUT
    NOTIF = lib.LYS_NOTIF
    ANYXML = lib.LYS_ANYXML
    ANYDATA = lib.LYS_ANYDATA
    AUGMENT = lib.LYS_AUGMENT
    USES = lib.LYS_USES
    GROUPING = lib.LYS_GROUPING
    KEYWORDS = {
        CONTAINER: "container",
        LEAF: "leaf",
        LEAFLIST: "leaf-list",
        LIST: "list",
        RPC: "rpc",
        ACTION: "action",
        INPUT: "input",
        OUTPUT: "output",
        NOTIF: "notification",
        ANYXML: "anyxml",
        ANYDATA: "anydata",
        AUGMENT: "augment",
        USES: "uses",
        GROUPING: "grouping",
    }

    __slots__ = ("context", "cdata", "module", "__dict__")

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        self.context = context
        self.cdata = ffi.cast("struct lysp_node *", cdata)
        self.module = module

    def parent(self) -> Optional["PNode"]:
        if self.cdata.parent == ffi.NULL:
            return None
        return PNode.new(self.context, self.cdata.parent, self.module)

    def nodetype(self) -> int:
        return self.cdata.nodetype

    def siblings(self) -> Iterator["PNode"]:
        for s in ly_list_iter(self.cdata.next):
            yield PNode.new(self.context, s, self.module)

    def name(self) -> str:
        return c2str(self.cdata.name)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def if_features(self) -> Iterator[IfFeatureExpr]:
        for f in ly_array_iter(self.cdata.iffeatures):
            yield IfFeatureExpr(self.context, f, list(self.module.features()))

    def extensions(self) -> Iterator["ExtensionParsed"]:
        for ext in ly_array_iter(self.cdata.exts):
            yield ExtensionParsed(self.context, ext, self.module)

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional["ExtensionParsed"]:
        for ext in self.extensions():
            if ext.name() != name:
                continue
            if prefix is not None and ext.module().name() != prefix:
                continue
            if arg_value is not None and ext.argument() != arg_value:
                continue
            return ext
        return None

    def config_set(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_SET_CONFIG)

    def config_false(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_CONFIG_R)

    def mandatory(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_MAND_TRUE)

    def deprecated(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_STATUS_OBSLT)

    def status(self) -> str:
        if self.cdata.flags & lib.LYS_STATUS_OBSLT:
            return "obsolete"
        if self.cdata.flags & lib.LYS_STATUS_DEPRC:
            return "deprecated"
        return "current"

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()

    NODETYPE_CLASS = {}

    @staticmethod
    def register(nodetype):
        def _decorator(nodeclass):
            PNode.NODETYPE_CLASS[nodetype] = nodeclass
            return nodeclass

        return _decorator

    @staticmethod
    def new(context: "libyang.Context", cdata, module: Module) -> "PNode":
        cdata = ffi.cast("struct lysp_node *", cdata)
        nodecls = PNode.NODETYPE_CLASS.get(cdata.nodetype, None)
        if nodecls is None:
            raise TypeError("node type %s not implemented" % cdata.nodetype)
        return nodecls(context, cdata, module)


# -------------------------------------------------------------------------------------
@PNode.register(PNode.CONTAINER)
class PContainer(PNode):
    __slots__ = ("cdata_container",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_container = ffi.cast("struct lysp_node_container *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_container.musts):
            yield Must(self.context, None, m)

    def when_condition(self) -> Optional[str]:
        if self.cdata_container.when == ffi.NULL:
            return None
        return c2str(self.cdata_container.when.cond)

    def presence(self) -> Optional[str]:
        return c2str(self.cdata_container.presence)

    def typedefs(self) -> Iterator[Typedef]:
        for t in ly_array_iter(self.cdata_container.typedefs):
            yield Typedef(self.context, t)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata_container.groupings):
            yield PGrouping(self.context, g, self.module)

    def children(self) -> Iterator[PNode]:
        for c in ly_list_iter(self.cdata_container.child):
            yield PNode.new(self.context, c, self.module)

    def actions(self) -> Iterator["PAction"]:
        for a in ly_list_iter(self.cdata_container.actions):
            yield PAction(self.context, a, self.module)

    def notifications(self) -> Iterator["PNotif"]:
        for n in ly_list_iter(self.cdata_container.notifs):
            yield PNotif(self.context, n, self.module)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.LEAF)
class PLeaf(PNode):
    __slots__ = ("cdata_leaf",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_leaf = ffi.cast("struct lysp_node_leaf *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_leaf.musts):
            yield Must(self.context, None, m)

    def when_condition(self) -> Optional[str]:
        if self.cdata_leaf.when == ffi.NULL:
            return None
        return c2str(self.cdata_leaf.when.cond)

    def type(self) -> PType:
        return PType(self.context, self.cdata_leaf.type, self.module)

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaf.units)

    def default(self) -> Optional[str]:
        return c2str(self.cdata_leaf.dflt.str)

    def is_key(self) -> bool:
        if self.cdata.flags & lib.LYS_KEY:
            return True
        return False


# -------------------------------------------------------------------------------------
@PNode.register(PNode.LEAFLIST)
class PLeafList(PNode):
    __slots__ = ("cdata_leaflist",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_leaflist = ffi.cast("struct lysp_node_leaflist *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_leaflist.musts):
            yield Must(self.context, None, m)

    def when_condition(self) -> Optional[str]:
        if self.cdata_leaflist.when == ffi.NULL:
            return None
        return c2str(self.cdata_leaflist.when.cond)

    def type(self) -> PType:
        return PType(self.context, self.cdata_leaflist.type, self.module)

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaflist.units)

    def defaults(self) -> Iterator[str]:
        for d in ly_array_iter(self.cdata_leaflist.dflts):
            yield c2str(d.str)

    def min_elements(self) -> int:
        return self.cdata_leaflist.min

    def max_elements(self) -> Optional[int]:
        return self.cdata_leaflist.max if self.cdata_leaflist.max != 0 else None

    def ordered(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_ORDBY_USER)


# -------------------------------------------------------------------------------------
@PNode.register(PNode.LIST)
class PList(PNode):
    __slots__ = ("cdata_list",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_list = ffi.cast("struct lysp_node_list *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_list.musts):
            yield Must(self.context, None, m)

    def when_condition(self) -> Optional[str]:
        if self.cdata_list.when == ffi.NULL:
            return None
        return c2str(self.cdata_list.when.cond)

    def key(self) -> Optional[str]:
        return c2str(self.cdata_list.key)

    def typedefs(self) -> Iterator[Typedef]:
        for t in ly_array_iter(self.cdata_list.typedefs):
            yield Typedef(self.context, t)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata_list.groupings):
            yield PGrouping(self.context, g, self.module)

    def children(self) -> Iterator[PNode]:
        for c in ly_list_iter(self.cdata_list.child):
            yield PNode.new(self.context, c, self.module)

    def actions(self) -> Iterator["PAction"]:
        for a in ly_list_iter(self.cdata_list.actions):
            yield PAction(self.context, a, self.module)

    def notifications(self) -> Iterator["PNotif"]:
        for n in ly_list_iter(self.cdata_list.notifs):
            yield PNotif(self.context, n, self.module)

    def uniques(self) -> Iterator[str]:
        for u in ly_array_iter(self.cdata_list.uniques):
            yield c2str(u.str)

    def min_elements(self) -> int:
        return self.cdata_list.min

    def max_elements(self) -> Optional[int]:
        return self.cdata_list.max if self.cdata_list.max != 0 else None

    def ordered(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_ORDBY_USER)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.CASE)
class PCase(PNode):
    __slots__ = ("cdata_case",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_case = ffi.cast("struct lysp_node_case *", cdata)

    def children(self) -> Iterator[PNode]:
        for c in ly_list_iter(self.cdata_case.child):
            yield PNode.new(self.context, c, self.module)

    def when_condition(self) -> Optional[str]:
        if self.cdata_case.when == ffi.NULL:
            return None
        return c2str(self.cdata_case.when.cond)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.CHOICE)
class PChoice(PNode):
    __slots__ = ("cdata_choice",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_choice = ffi.cast("struct lysp_node_choice *", cdata)

    def children(self) -> Iterator[PCase]:
        for c in ly_list_iter(self.cdata_choice.child):
            yield PCase(self.context, c, self.module)

    def when_condition(self) -> Optional[str]:
        if self.cdata_choice.when == ffi.NULL:
            return None
        return c2str(self.cdata_choice.when.cond)

    def default(self) -> Optional[str]:
        return c2str(self.cdata_choice.dflt.str)

    def __iter__(self) -> Iterator[PCase]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.ANYXML)
@PNode.register(PNode.ANYDATA)
class PAnydata(PNode):
    __slots__ = ("cdata_anydata",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_anydata = ffi.cast("struct lysp_node_anydata *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_anydata.musts):
            yield Must(self.context, None, m)

    def when_condition(self) -> Optional[str]:
        if self.cdata_anydata.when == ffi.NULL:
            return None
        return c2str(self.cdata_anydata.when.cond)


# -------------------------------------------------------------------------------------
@PNode.register(PNode.AUGMENT)
class PAugment(PNode):
    __slots__ = ("cdata_augment",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_augment = ffi.cast("struct lysp_node_augment *", cdata)

    def children(self) -> Iterator["PNode"]:
        for c in ly_list_iter(self.cdata_augment.child):
            yield PNode.new(self.context, c, self.module)

    def when_condition(self) -> Optional[str]:
        if self.cdata_augment.when == ffi.NULL:
            return None
        return c2str(self.cdata_augment.when.cond)

    def actions(self) -> Iterator["PAction"]:
        for a in ly_list_iter(self.cdata_augment.actions):
            yield PAction(self.context, a, self.module)

    def notifications(self) -> Iterator["PNotif"]:
        for n in ly_list_iter(self.cdata_augment.notifs):
            yield PNotif(self.context, n, self.module)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.USES)
class PUses(PNode):
    __slots__ = ("cdata_uses",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_uses = ffi.cast("struct lysp_node_uses *", cdata)

    def refines(self) -> Iterator[PRefine]:
        for r in ly_array_iter(self.cdata_uses.refines):
            yield PRefine(self.context, r, self.module)

    def augments(self) -> Iterator[PAugment]:
        for a in ly_list_iter(self.cdata_uses.augments):
            yield PAugment(self.context, a, self.module)

    def when_condition(self) -> Optional[str]:
        if self.cdata_uses.when == ffi.NULL:
            return None
        return c2str(self.cdata_uses.when.cond)


# -------------------------------------------------------------------------------------
class PActionInOut(PNode):
    __slots__ = ("cdata_action_inout",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_action_inout = ffi.cast("struct lysp_node_action_inout *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_action_inout.musts):
            yield Must(self.context, None, m)

    def typedefs(self) -> Iterator[Typedef]:
        for t in ly_array_iter(self.cdata_action_inout.typedefs):
            yield Typedef(self.context, t)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata_action_inout.groupings):
            yield PGrouping(self.context, g, self.module)

    def children(self) -> Iterator[PNode]:
        for c in ly_list_iter(self.cdata_action_inout.child):
            yield PNode.new(self.context, c, self.module)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.RPC)
@PNode.register(PNode.ACTION)
class PAction(PNode):
    __slots__ = ("cdata_action",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_action = ffi.cast("struct lysp_node_action *", cdata)

    def typedefs(self) -> Iterator[Typedef]:
        for t in ly_array_iter(self.cdata_action.typedefs):
            yield Typedef(self.context, t)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata_action.groupings):
            yield PGrouping(self.context, g, self.module)

    def input(self) -> PActionInOut:
        ptr = ffi.addressof(self.cdata_action.input)
        return PActionInOut(self.context, ptr, self.module)

    def output(self) -> PActionInOut:
        ptr = ffi.addressof(self.cdata_action.output)
        return PActionInOut(self.context, ptr, self.module)


# -------------------------------------------------------------------------------------
@PNode.register(PNode.NOTIF)
class PNotif(PNode):
    __slots__ = ("cdata_notif",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_notif = ffi.cast("struct lysp_node_notif *", cdata)

    def musts(self) -> Iterator[Must]:
        for m in ly_array_iter(self.cdata_notif.musts):
            yield Must(self.context, None, m)

    def typedefs(self) -> Iterator[Typedef]:
        for t in ly_array_iter(self.cdata_notif.typedefs):
            yield Typedef(self.context, t)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata_notif.groupings):
            yield PGrouping(self.context, g, self.module)

    def children(self) -> Iterator[PNode]:
        for c in ly_list_iter(self.cdata_notif.child):
            yield PNode.new(self.context, c, self.module)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()


# -------------------------------------------------------------------------------------
@PNode.register(PNode.GROUPING)
class PGrouping(PNode):
    __slots__ = ("cdata_grouping",)

    def __init__(self, context: "libyang.Context", cdata, module: Module) -> None:
        super().__init__(context, cdata, module)
        self.cdata_grouping = ffi.cast("struct lysp_node_grp *", cdata)

    def typedefs(self) -> Iterator[Typedef]:
        for t in ly_array_iter(self.cdata_grouping.typedefs):
            yield Typedef(self.context, t)

    def groupings(self) -> Iterator["PGrouping"]:
        for g in ly_list_iter(self.cdata_grouping.groupings):
            yield PGrouping(self.context, g, self.module)

    def children(self) -> Iterator[PNode]:
        for c in ly_list_iter(self.cdata_grouping.child):
            yield PNode.new(self.context, c, self.module)

    def actions(self) -> Iterator[PAction]:
        for a in ly_list_iter(self.cdata_grouping.actions):
            yield PAction(self.context, a, self.module)

    def notifications(self) -> Iterator[PNotif]:
        for n in ly_list_iter(self.cdata_grouping.notifs):
            yield PNotif(self.context, n, self.module)

    def __iter__(self) -> Iterator[PNode]:
        return self.children()
