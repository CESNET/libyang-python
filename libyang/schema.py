# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

from contextlib import suppress
from typing import IO, Any, Dict, Iterator, Optional, Tuple, Union

from _libyang import ffi, lib
from .util import IOType, c2str, init_output, ly_array_iter, str2c


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

    __slots__ = ("context", "cdata")

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

    def __iter__(self) -> Iterator["SNode"]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator["SNode"]:
        return iter_children(self.context, self.cdata, types=types)

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
        )


# -------------------------------------------------------------------------------------
class Revision:

    __slots__ = ("context", "cdata", "module")

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
class Extension:

    __slots__ = ("context", "cdata")

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


# -------------------------------------------------------------------------------------
class _EnumBit:

    __slots__ = ("context", "cdata")

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
class Type:

    __slots__ = ("context", "cdata", "cdata_parsed")

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

    def union_types(self) -> Iterator["Type"]:
        if self.cdata.basetype != self.UNION:
            return
        t = ffi.cast("struct lysc_type_union *", self.cdata)
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

    def module(self) -> Module:
        # TODO: pointer to the parsed module wehere is the type defined is in self.cdata_parsed.pmod
        # however there is no way how to get name of the module from lysp_module
        if not self.cdata.der.module:
            return None
        return Module(self.context, self.cdata.der.module)

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


# -------------------------------------------------------------------------------------
class Feature:

    __slots__ = ("context", "cdata")

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

    __slots__ = ("context", "cdata", "module_features", "compiled")

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
            raise Exception("No feature %s in module" % name)

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
class SNode:

    __slots__ = ("context", "cdata", "cdata_parsed")

    CONTAINER = lib.LYS_CONTAINER
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

    def schema_path(self) -> str:
        try:
            s = lib.lysc_path(self.cdata, lib.LYSC_PATH_LOG, ffi.NULL, 0)
            return c2str(s)
        finally:
            lib.free(s)

    def data_path(self, key_placeholder: str = "'%s'") -> str:
        try:
            s = lib.lysc_path(self.cdata, lib.LYSC_PATH_DATA_PATTERN, ffi.NULL, 0)
            val = c2str(s)
            if key_placeholder != "'%s'":
                val = val.replace("'%s'", key_placeholder)
            return val
        finally:
            lib.free(s)

    def extensions(self) -> Iterator[ExtensionCompiled]:
        ext = ffi.cast("struct lysc_ext_instance *", self.cdata.exts)
        if ext == ffi.NULL:
            return
        for extension in ly_array_iter(ext):
            yield ExtensionCompiled(self.context, extension)

    def must_conditions(self) -> Iterator[str]:
        return iter(())

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

    def default(self) -> Union[None, bool, int, str]:
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
        return val

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaf.units)

    def type(self) -> Type:
        return Type(self.context, self.cdata_leaf.type, self.cdata_leaf_parsed.type)

    def is_key(self) -> bool:
        if self.cdata_leaf.flags & lib.LYS_KEY:
            return True
        return False

    def must_conditions(self) -> Iterator[str]:
        pdata = self.cdata_leaf_parsed
        if pdata.musts == ffi.NULL:
            return
        for must in ly_array_iter(pdata.musts):
            yield c2str(must.arg.str)

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

    def defaults(self) -> Iterator[str]:
        if self.cdata_leaflist.dflts == ffi.NULL:
            return
        arr_length = ffi.cast("uint64_t *", self.cdata_leaflist.dflts)[-1]
        for i in range(arr_length):
            val = lib.lyd_value_get_canonical(
                self.context.cdata, self.cdata_leaflist.dflts[i]
            )
            if not val:
                yield None
            ret = c2str(val)
            val_type = self.cdata_leaflist.dflts[i].realtype
            if val_type == Type.BOOL:
                ret = val == "true"
            elif val_type in Type.NUM_TYPES:
                ret = int(val)
            yield ret

    def must_conditions(self) -> Iterator[str]:
        pdata = self.cdata_leaflist_parsed
        if pdata.musts == ffi.NULL:
            return
        for must in ly_array_iter(pdata.musts):
            yield c2str(must.arg.str)

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

    def must_conditions(self) -> Iterator[str]:
        pdata = self.cdata_container_parsed
        if pdata.musts == ffi.NULL:
            return
        for must in ly_array_iter(pdata.musts):
            yield c2str(must.arg.str)

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, types=types)


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
        self, skip_keys: bool = False, types: Optional[Tuple[int, ...]] = None
    ) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, skip_keys=skip_keys, types=types)

    def keys(self) -> Iterator[SNode]:
        node = lib.lysc_node_child(self.cdata)
        while node:
            if node.flags & lib.LYS_KEY:
                yield SLeaf(self.context, node)
            node = node.next

    def must_conditions(self) -> Iterator[str]:
        pdata = self.cdata_list_parsed
        if pdata.musts == ffi.NULL:
            return
        for must in ly_array_iter(pdata.musts):
            yield c2str(must.arg.str)

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
        yield from iter_children(
            self.context, self.cdata, types=types, options=lib.LYS_GETNEXT_OUTPUT
        )


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
def iter_children(
    context: "libyang.Context",
    parent,  # C type: Union["struct lys_module *", "struct lys_node *"]
    skip_keys: bool = False,
    types: Optional[Tuple[int, ...]] = None,
    options: int = 0,
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
        module = parent.compiled
        parent = ffi.NULL
    else:
        module = ffi.NULL

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
