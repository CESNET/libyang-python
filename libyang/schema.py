# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

from typing import IO, Any, Dict, Iterator, Optional, Tuple, Union

from _libyang import ffi, lib
from .util import c2str, deprecated, str2c


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
    if fmt_string == "info":
        return lib.LYS_OUT_INFO
    if fmt_string == "json":
        return lib.LYS_OUT_JSON
    raise ValueError("unknown schema output format: %r" % fmt_string)


# -------------------------------------------------------------------------------------
class Module:

    __slots__ = ("context", "cdata")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_module *"

    @property
    def _module(self):
        deprecated("_module", "cdata", "2.0.0")
        return self.cdata

    def name(self) -> str:
        return c2str(self.cdata.name)

    def prefix(self) -> str:
        return c2str(self.cdata.prefix)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def filepath(self) -> Optional[str]:
        return c2str(self.cdata.filepath)

    def implemented(self) -> bool:
        return bool(lib.lypy_module_implemented(self.cdata))

    def feature_enable(self, name: str) -> None:
        ret = lib.lys_features_enable(self.cdata, str2c(name))
        if ret != 0:
            raise self.context.error("no such feature: %r" % name)

    def feature_enable_all(self) -> None:
        self.feature_enable("*")

    def feature_disable(self, name: str) -> None:
        ret = lib.lys_features_disable(self.cdata, str2c(name))
        if ret != 0:
            raise self.context.error("no such feature: %r" % name)

    def feature_disable_all(self) -> None:
        self.feature_disable("*")

    def feature_state(self, name: str) -> bool:
        ret = lib.lys_features_state(self.cdata, str2c(name))
        if ret < 0:
            raise self.context.error("no such feature: %r" % name)
        return bool(ret)

    def features(self) -> Iterator["Feature"]:
        for i in range(self.cdata.features_size):
            yield Feature(self.context, self.cdata.features[i])

    def get_feature(self, name: str) -> "Feature":
        for f in self.features():
            if f.name() == name:
                return f
        raise self.context.error("no such feature: %r" % name)

    def revisions(self) -> Iterator["Revision"]:
        for i in range(self.cdata.rev_size):
            yield Revision(self.context, self.cdata.rev[i])

    def __iter__(self) -> Iterator["SNode"]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator["SNode"]:
        return iter_children(self.context, self.cdata, types=types)

    def __str__(self) -> str:
        return self.name()

    def print_mem(
        self, fmt: str = "tree", path: Optional[str] = None
    ) -> Union[str, bytes]:
        fmt = schema_out_format(fmt)
        buf = ffi.new("char **")
        ret = lib.lys_print_mem(buf, self.cdata, fmt, str2c(path), 0, 0)
        if ret != 0:
            raise self.context.error("cannot print module")
        try:
            return c2str(buf[0])
        finally:
            lib.free(buf[0])

    def print_file(
        self, fileobj: IO, fmt: str = "tree", path: Optional[str] = None
    ) -> None:
        fmt = schema_out_format(fmt)
        ret = lib.lys_print_fd(fileobj.fileno(), self.cdata, fmt, str2c(path), 0, 0)
        if ret != 0:
            raise self.context.error("cannot print module")

    def parse_data_dict(
        self,
        dic: Dict[str, Any],
        data: bool = False,
        config: bool = False,
        get: bool = False,
        getconfig: bool = False,
        edit: bool = False,
        rpc: bool = False,
        rpcreply: bool = False,
        strict: bool = False,
        no_yanglib: bool = False,
        validate: bool = True,
    ) -> "libyang.data.DNode":
        """
        Convert a python dictionary to a DNode object following the schema of this
        module. The returned value is always a top-level data node (i.e.: without
        parent).

        :arg dic:
            The python dictionary to convert.
        :arg data:
            Complete datastore content with configuration as well as state data. To
            handle possibly missing (but by default required) ietf-yang-library data,
            use no_yanglib=True.
        :arg config:
            Complete datastore without state data.
        :arg get:
            Data content from a reply message to the NETCONF <get> operation.
        :arg getconfig:
            Data content from a reply message to the NETCONF <get-config> operation.
        :arg edit:
            Content of the NETCONF <edit-config> config element.
        :arg rpc:
            Data represents RPC or action input parameters.
        :arg rpcreply:
            Data represents RPC or action output parameters.
        :arg strict:
            Instead of ignoring (with a warning message) data without schema definition,
            raise an error.
        :arg no_yanglib:
            Ignore (possibly) missing ietf-yang-library data. Applicable only with
            data=True.
        :arg validate:
            If False, do not validate the created data tree.
        """
        from .data import dict_to_dnode  # circular import

        return dict_to_dnode(
            dic,
            self,
            parent=None,
            data=data,
            config=config,
            get=get,
            getconfig=getconfig,
            edit=edit,
            rpc=rpc,
            rpcreply=rpcreply,
            strict=strict,
            no_yanglib=no_yanglib,
            validate=validate,
        )


# -------------------------------------------------------------------------------------
class Revision:

    __slots__ = ("context", "cdata")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_revision *"

    @property
    def _rev(self):
        deprecated("_rev", "cdata", "2.0.0")
        return self.cdata

    def date(self) -> str:
        return c2str(self.cdata.date)

    def description(self) -> Optional[str]:
        return c2str(self.cdata.dsc)

    def reference(self) -> Optional[str]:
        return c2str(self.cdata.ref)

    def extensions(self) -> Iterator["Extension"]:
        for i in range(self.cdata.ext_size):
            yield Extension(self.context, self.cdata.ext[i])

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional["Extension"]:
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

    __slots__ = ("context", "cdata", "cdata_def")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_ext_instance *"
        self.cdata_def = getattr(cdata, "def")

    @property
    def _ext(self):
        deprecated("_ext", "cdata", "2.0.0")

    @property
    def _def(self):
        deprecated("_def", "cdata_def", "2.0.0")

    def name(self) -> str:
        return c2str(self.cdata_def.name)

    def argument(self) -> Optional[str]:
        return c2str(self.cdata.arg_value)

    def module(self) -> Module:
        module_p = lib.lys_main_module(self.cdata_def.module)
        if not module_p:
            raise self.context.error("cannot get module")
        return Module(self.context, module_p)

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class Type:

    __slots__ = ("context", "cdata")

    DER = lib.LY_TYPE_DER
    BINARY = lib.LY_TYPE_BINARY
    BITS = lib.LY_TYPE_BITS
    BOOL = lib.LY_TYPE_BOOL
    DEC64 = lib.LY_TYPE_DEC64
    EMPTY = lib.LY_TYPE_EMPTY
    ENUM = lib.LY_TYPE_ENUM
    IDENT = lib.LY_TYPE_IDENT
    INST = lib.LY_TYPE_INST
    LEAFREF = lib.LY_TYPE_LEAFREF
    STRING = lib.LY_TYPE_STRING
    UNION = lib.LY_TYPE_UNION
    INT8 = lib.LY_TYPE_INT8
    UINT8 = lib.LY_TYPE_UINT8
    INT16 = lib.LY_TYPE_INT16
    UINT16 = lib.LY_TYPE_UINT16
    INT32 = lib.LY_TYPE_INT32
    UINT32 = lib.LY_TYPE_UINT32
    INT64 = lib.LY_TYPE_INT64
    UINT64 = lib.LY_TYPE_UINT64
    BASENAMES = {
        DER: "derived",
        BINARY: "binary",
        BITS: "bits",
        BOOL: "boolean",
        DEC64: "decimal64",
        EMPTY: "empty",
        ENUM: "enumeration",
        IDENT: "identityref",
        INST: "instance-id",
        LEAFREF: "leafref",
        STRING: "string",
        UNION: "union",
        INT8: "int8",
        UINT8: "uint8",
        INT16: "int16",
        UINT16: "uint16",
        INT32: "int32",
        UINT32: "uint32",
        INT64: "int64",
        UINT64: "uint64",
    }

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_type *"

    @property
    def _type(self):
        deprecated("_type", "cdata", "2.0.0")
        return self.cdata

    def get_bases(self) -> Iterator["Type"]:
        if self.cdata.base == lib.LY_TYPE_DER:
            yield from self.derived_type().get_bases()
        elif self.cdata.base == lib.LY_TYPE_LEAFREF:
            yield from self.leafref_type().get_bases()
        elif self.cdata.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.get_bases()
        else:  # builtin type
            yield self

    def name(self) -> str:
        if self.cdata.der:
            return c2str(self.cdata.der.name)
        return self.basename()

    def description(self) -> Optional[str]:
        if self.cdata.der:
            return c2str(self.cdata.der.dsc)
        return None

    def base(self) -> int:
        return self.cdata.base

    def bases(self) -> Iterator[int]:
        for b in self.get_bases():
            yield b.base()

    def basename(self) -> str:
        return self.BASENAMES.get(self.cdata.base, "unknown")

    def basenames(self) -> Iterator[str]:
        for b in self.get_bases():
            yield b.basename()

    def derived_type(self) -> Optional["Type"]:
        if not self.cdata.der:
            return None
        return Type(self.context, ffi.addressof(self.cdata.der.type))

    def leafref_type(self) -> Optional["Type"]:
        if self.cdata.base != self.LEAFREF:
            return None
        lref = self.cdata.info.lref
        return Type(self.context, ffi.addressof(lref.target.type))

    def union_types(self) -> Iterator["Type"]:
        if self.cdata.base != self.UNION:
            return
        t = self.cdata
        while t.info.uni.count == 0:
            t = ffi.addressof(t.der.type)
        for i in range(t.info.uni.count):
            yield Type(self.context, t.info.uni.types[i])

    def enums(self) -> Iterator[Tuple[str, Optional[str]]]:
        if self.cdata.base != self.ENUM:
            return
        t = self.cdata
        while t.info.enums.count == 0:
            t = ffi.addressof(t.der.type)
        for i in range(t.info.enums.count):
            e = t.info.enums.enm[i]
            yield c2str(e.name), c2str(e.dsc)

    def all_enums(self) -> Iterator[Tuple[str, Optional[str]]]:
        for b in self.get_bases():
            yield from b.enums()

    def bits(self) -> Iterator[Tuple[str, Optional[str]]]:
        if self.cdata.base != self.BITS:
            return
        t = self.cdata
        while t.info.bits.count == 0:
            t = ffi.addressof(t.der.type)
        for i in range(t.info.bits.count):
            b = t.info.bits.bit[i]
            yield c2str(b.name), c2str(b.dsc)

    def all_bits(self) -> Iterator[Tuple[str, Optional[str]]]:
        for b in self.get_bases():
            yield from b.bits()

    NUM_TYPES = frozenset((INT8, INT16, INT32, INT64, UINT8, UINT16, UINT32, UINT64))

    def range(self) -> Optional[str]:
        if self.cdata.base in self.NUM_TYPES and self.cdata.info.num.range:
            return c2str(self.cdata.info.num.range.expr)
        if self.cdata.base == self.DEC64 and self.cdata.info.dec64.range:
            return c2str(self.cdata.info.dec64.range.expr)
        if self.cdata.der:
            return self.derived_type().range()
        return None

    def all_ranges(self) -> Iterator[str]:
        if self.cdata.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_ranges()
        else:
            rng = self.range()
            if rng is not None:
                yield rng

    STR_TYPES = frozenset((STRING, BINARY, ENUM, IDENT, BITS))

    def length(self) -> Optional[str]:
        if self.cdata.base == self.STRING and self.cdata.info.str.length:
            return c2str(self.cdata.info.str.length.expr)
        if self.cdata.base == self.BINARY and self.cdata.info.binary.length:
            return c2str(self.cdata.info.binary.length.expr)
        if self.cdata.der:
            return self.derived_type().length()
        return None

    def all_lengths(self) -> Iterator[str]:
        if self.cdata.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_lengths()
        else:
            length = self.length()
            if length is not None:
                yield length

    def patterns(self) -> Iterator[Tuple[str, bool]]:
        if self.cdata.base != self.STRING:
            return
        for i in range(self.cdata.info.str.pat_count):
            p = self.cdata.info.str.patterns[i]
            if not p:
                continue
            # in case of pattern restriction, the first byte has a special meaning:
            # 0x06 (ACK) for regular match and 0x15 (NACK) for invert-match
            invert_match = p.expr[0] == 0x15
            # yield tuples like:
            #     ('[a-zA-Z_][a-zA-Z0-9\-_.]*', False)
            #     ('[xX][mM][lL].*', True)
            yield c2str(p.expr + 1), invert_match
        if self.cdata.der:
            yield from self.derived_type().patterns()

    def all_patterns(self) -> Iterator[Tuple[str, bool]]:
        if self.cdata.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                yield from t.all_patterns()
        else:
            yield from self.patterns()

    def module(self) -> Module:
        if not self.cdata.der.module:
            return None
        module_p = lib.lys_main_module(self.cdata.der.module)
        if not module_p:
            raise self.context.error("cannot get module")
        return Module(self.context, module_p)

    def extensions(self) -> Iterator[Extension]:
        for i in range(self.cdata.ext_size):
            yield Extension(self.context, self.cdata.ext[i])
        if self.cdata.parent:
            for i in range(self.cdata.parent.ext_size):
                yield Extension(self.context, self.cdata.parent.ext[i])

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional[Extension]:
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
        self.cdata = cdata  # C type: "struct lys_feature *"

    @property
    def _feature(self):
        deprecated("_feature", "cdata", "2.0.0")
        return self.cdata

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
        for i in range(self.cdata.iffeature_size):
            yield IfFeatureExpr(self.context, self.cdata.iffeature[i])

    def module(self) -> Module:
        module_p = lib.lys_main_module(self.cdata.module)
        if not module_p:
            raise self.context.error("cannot get module")
        return Module(self.context, module_p)

    def __str__(self):
        return self.name()


# -------------------------------------------------------------------------------------
class IfFeatureExpr:

    __slots__ = ("context", "cdata")

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_iffeature *"

    @property
    def _iffeature(self):
        deprecated("_iffeature", "cdata", "2.0.0")
        return self.cdata

    def _get_operator(self, position: int) -> int:
        # the ->exp field is a 2bit array of operator values stored under a uint8_t C
        # array.
        mask = 0x3  # 2bits mask
        shift = 2 * (position % 4)
        item = self.cdata.expr[position // 4]
        result = item & (mask << shift)
        return result >> shift

    def _operands(self) -> Iterator[Union["IfFeature", type]]:
        op_index = 0
        ft_index = 0
        expected = 1
        while expected > 0:
            operator = self._get_operator(op_index)
            op_index += 1
            if operator == lib.LYS_IFF_F:
                yield IfFeature(self.context, self.cdata.features[ft_index])
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

    @property
    def _feature(self):
        deprecated("_feature", "cdata", "2.0.0")
        return self.cdata

    def feature(self) -> Feature:
        return Feature(self.context, self.cdata)

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

    def dump(self, indent: int = 0) -> str:
        s = " " * indent + "OR\n"
        s += self.a.dump(indent + 1)
        s += self.b.dump(indent + 1)
        return s

    def __str__(self):
        return "(%s OR %s)" % (self.a, self.b)


# -------------------------------------------------------------------------------------
class SNode:

    __slots__ = ("context", "cdata")

    CONTAINER = lib.LYS_CONTAINER
    LEAF = lib.LYS_LEAF
    LEAFLIST = lib.LYS_LEAFLIST
    LIST = lib.LYS_LIST
    RPC = lib.LYS_RPC
    ACTION = lib.LYS_ACTION
    INPUT = lib.LYS_INPUT
    OUTPUT = lib.LYS_OUTPUT
    KEYWORDS = {
        CONTAINER: "container",
        LEAF: "leaf",
        LEAFLIST: "leaf-list",
        LIST: "list",
        RPC: "rpc",
        ACTION: "action",
        INPUT: "input",
        OUTPUT: "output",
    }

    def __init__(self, context: "libyang.Context", cdata):
        self.context = context
        self.cdata = cdata  # C type: "struct lys_node *"

    @property
    def _node(self):
        deprecated("_node", "cdata", "2.0.0")
        return self.cdata

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
        return bool(self.cdata.flags & lib.LYS_CONFIG_SET)

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
        module_p = lib.lys_node_module(self.cdata)
        if not module_p:
            raise self.context.error("cannot get module")
        return Module(self.context, module_p)

    def schema_path(self) -> str:
        try:
            s = lib.lys_path(self.cdata, 0)
            return c2str(s)
        finally:
            lib.free(s)

    def data_path(self, key_placeholder: str = "'%s'") -> str:
        try:
            s = lib.lys_data_path_pattern(self.cdata, str2c(key_placeholder))
            return c2str(s)
        finally:
            lib.free(s)

    def extensions(self) -> Iterator[Extension]:
        for i in range(self.cdata.ext_size):
            yield Extension(self.context, self.cdata.ext[i])

    def must_conditions(self) -> Iterator[str]:
        return iter(())

    def get_extension(
        self, name: str, prefix: Optional[str] = None, arg_value: Optional[str] = None
    ) -> Optional[Extension]:
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
        for i in range(self.cdata.iffeature_size):
            yield IfFeatureExpr(self.context, self.cdata.iffeature[i])

    def parent(self) -> Optional["SNode"]:
        parent_p = lib.lys_parent(self.cdata)
        while parent_p and parent_p.nodetype not in SNode.NODETYPE_CLASS:
            parent_p = lib.lys_parent(parent_p)
        if parent_p:
            return SNode.new(self.context, parent_p)
        return None

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
        cdata = ffi.cast("struct lys_node *", cdata)
        nodecls = SNode.NODETYPE_CLASS.get(cdata.nodetype, None)
        if nodecls is None:
            raise NotImplementedError("node type %s not implemented" % cdata.nodetype)
        return nodecls(context, cdata)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.LEAF)
class SLeaf(SNode):

    __slots__ = SNode.__slots__ + ("cdata_leaf",)

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_leaf = ffi.cast("struct lys_node_leaf *", cdata)

    @property
    def _leaf(self):
        deprecated("_leaf", "cdata_leaf", "2.0.0")
        return self.cdata_leaf

    def default(self) -> Optional[str]:
        return c2str(self.cdata_leaf.dflt)

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaf.units)

    def type(self) -> Type:
        return Type(self.context, ffi.addressof(self.cdata_leaf.type))

    def is_key(self) -> bool:
        if lib.lys_is_key(self.cdata_leaf, ffi.NULL):
            return True
        return False

    def must_conditions(self) -> Iterator[str]:
        for i in range(self.cdata_leaf.must_size):
            yield c2str(self.cdata_leaf.must[i].expr)

    def __str__(self):
        return "%s %s" % (self.name(), self.type().name())


# -------------------------------------------------------------------------------------
@SNode.register(SNode.LEAFLIST)
class SLeafList(SNode):

    __slots__ = SNode.__slots__ + ("cdata_leaflist",)

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_leaflist = ffi.cast("struct lys_node_leaflist *", cdata)

    @property
    def _leaflist(self):
        deprecated("_leaflist", "cdata_leaflist", "2.0.0")
        return self.cdata_leaflist

    def ordered(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_USERORDERED)

    def units(self) -> Optional[str]:
        return c2str(self.cdata_leaflist.units)

    def type(self) -> Type:
        return Type(self.context, ffi.addressof(self.cdata_leaflist.type))

    def defaults(self) -> Iterator[str]:
        for i in range(self.cdata_leaflist.dflt_size):
            yield c2str(self.cdata_leaflist.dflt[i])

    def must_conditions(self) -> Iterator[str]:
        for i in range(self.cdata_leaflist.must_size):
            yield c2str(self.cdata_leaflist.must[i].expr)

    def __str__(self):
        return "%s %s" % (self.name(), self.type().name())


# -------------------------------------------------------------------------------------
@SNode.register(SNode.CONTAINER)
class SContainer(SNode):

    __slots__ = SNode.__slots__ + ("cdata_container",)

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_container = ffi.cast("struct lys_node_container *", cdata)

    @property
    def _container(self):
        deprecated("_container", "cdata_container", "2.0.0")
        return self.cdata_container

    def presence(self) -> Optional[str]:
        return c2str(self.cdata_container.presence)

    def must_conditions(self) -> Iterator[str]:
        for i in range(self.cdata_container.must_size):
            yield c2str(self.cdata_container.must[i].expr)

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, types=types)


# -------------------------------------------------------------------------------------
@SNode.register(SNode.LIST)
class SList(SNode):

    __slots__ = SNode.__slots__ + ("cdata_list",)

    def __init__(self, context: "libyang.Context", cdata):
        super().__init__(context, cdata)
        self.cdata_list = ffi.cast("struct lys_node_list *", cdata)

    @property
    def _list(self):
        deprecated("_list", "cdata_list", "2.0.0")
        return self.cdata_list

    def ordered(self) -> bool:
        return bool(self.cdata.flags & lib.LYS_USERORDERED)

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(
        self, skip_keys: bool = False, types: Optional[Tuple[int, ...]] = None
    ) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, skip_keys=skip_keys, types=types)

    def keys(self) -> Iterator[SNode]:
        for i in range(self.cdata_list.keys_size):
            node = ffi.cast("struct lys_node *", self.cdata_list.keys[i])
            yield SLeaf(self.context, node)

    def must_conditions(self) -> Iterator[str]:
        for i in range(self.cdata_list.must_size):
            yield c2str(self.cdata_list.must[i].expr)

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
        try:
            return next(
                iter_children(
                    self.context,
                    self.cdata,
                    types=(self.INPUT,),
                    options=lib.LYS_GETNEXT_WITHINOUT,
                )
            )
        except StopIteration:
            return None

    def output(self) -> Optional[SRpcInOut]:
        try:
            return next(
                iter_children(
                    self.context,
                    self.cdata,
                    types=(self.OUTPUT,),
                    options=lib.LYS_GETNEXT_WITHINOUT,
                )
            )
        except StopIteration:
            return None

    def __iter__(self) -> Iterator[SNode]:
        return self.children()

    def children(self, types: Optional[Tuple[int, ...]] = None) -> Iterator[SNode]:
        return iter_children(self.context, self.cdata, types=types)


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
        )

    def _skip(node) -> bool:
        if node.nodetype not in types:
            return True
        if not skip_keys:
            return False
        if node.nodetype != lib.LYS_LEAF:
            return False
        leaf = ffi.cast("struct lys_node_leaf *", node)
        if lib.lys_is_key(leaf, ffi.NULL):
            return True
        return False

    if ffi.typeof(parent) == ffi.typeof("struct lys_module *"):
        module = parent
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
