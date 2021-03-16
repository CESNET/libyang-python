# Copyright (c) 2020 CESNET, z.s.p.o.
# SPDX-License-Identifier: BSD-3-Clause
# Author David Sedlák
from typing import Iterator, Union, TYPE_CHECKING, Tuple

from _libyang import lib, ffi

from .utils import Node, SchemaFactory, WrapperBase
from .schema import (
    SModule,
    SWrapperHasName,
    SWrapperHasDesRef,
    SWrapperHasStatus,
    SWrapperHasConfig,
    SWrapperHasUnits,
    SWrapperHasEmsgEpptag,
    SWrapperHasArgument,
    SWrapperHasModule,
    ored_options,
)


class SCWrapperHasMinMax(WrapperBase):
    """Mixin for wrappers over lysc cdata with min and max members

    Provides min and max getters
    """

    @property
    def min(self) -> int:
        """Get min value"""

        return self._cdata.min

    @property
    def max(self) -> int:
        """Get max value"""

        return self._cdata.max


class SCWrapperHasIffeatures(WrapperBase):
    """Mixin for wrappers over lysc cdata with iffeatures member

    Provides iffeatures getter"""

    def iffeatures(self) -> Iterator["SCIffeature"]:
        """Get if-feature expressions.

        Returned value is generator."""

        return self._context.sf.arr2gen(self._cdata.iffeatures)


class SCWrapperHasExts(WrapperBase):
    """Mixin for wrappers over lysc cdata with exts member

    Provides extension_instances getter"""

    def extension_instances(self) -> Iterator["SCExtensionInstance"]:
        return self._context.sf.arr2gen(self._cdata.exts)


class SCWrapperHasChild(WrapperBase):
    """Mixin for wrappers over lysc cdata with child member

    Provides childs getter and makes the mixin iterable"""

    def childs(
        self,
        intonpcont: bool = False,
        nochoice: bool = False,
        output: bool = False,
        withcase: bool = False,
        withchoice: bool = False,
    ) -> Iterator["SCNode"]:
        """Get schema tree child nodes that can be instantiated in
        a data tree. Returned node can be from an augment"""

        opts = ored_options(
            intonpcont, nochoice, output, withcase, withchoice
        )
        scmod = self._cdata.module.compiled
        parent = ffi.cast("struct lysc_node *", self._cdata)
        next_node = lib.lys_getnext(ffi.NULL, parent, scmod, opts)
        while next_node:
            yield self.context.sf.wrap(next_node)
            next_node = lib.lys_getnext(next_node, parent, scmod, opts)

    __iter__ = childs


class SCWrapperHasData(WrapperBase):
    """Mixin for wrappers over lysc cdata with data member

    Provides childs getter and makes the mixin iterable"""

    def childs(
        self,
        intonpcont: bool = False,
        nochoice: bool = False,
        output: bool = False,
        withcase: bool = False,
        withchoice: bool = False,
    ) -> Iterator["SCNode"]:
        """Get schema tree child nodes that can be instantiated in
        a data tree. Returned node can be from an augment"""

        opts = ored_options(
            intonpcont, nochoice, output, withcase, withchoice
        )
        scmod = self._cdata.module.compiled
        parent = ffi.cast("struct lysc_node *", self._cdata)
        next_node = lib.lys_getnext(ffi.NULL, parent, scmod, opts)
        while next_node:
            yield self.context.sf.wrap(next_node)
            next_node = lib.lys_getnext(next_node, parent, scmod, opts)

    __iter__ = childs


class SCWrapperHasMusts(WrapperBase):
    """Mixin for wrappers over lysc cdata with musts member"""

    def musts(self) -> Iterator["SCMust"]:
        return self._context.sf.arr2gen(self._cdata.musts)


class SCWrapperHasActions(WrapperBase):
    """Mixin for wrappers over lysc cdata with action member"""

    def actions(self) -> Iterator["SCAction"]:
        return self._context.sf.arr2gen(self._cdata.actions)


class SCWrapperHasNotifs(WrapperBase):
    """Mixin for wrappers over lysc cdata with notifs member"""

    def notifications(self) -> Iterator["SCNotification"]:
        """Statements compiled notification statements"""

        return self._context.sf.arr2gen(self._cdata.notifs)


class SCWrapperHasCases(WrapperBase):
    """Mixin for wrappers over lysc cdata with cases member"""

    def cases(self) -> Iterator["SCCase"]:
        """Statements compiled case statements"""

        return self._context.sf.ll2gen(self._cdata.cases)


class SCWrapperHasType(WrapperBase):
    """Mixin for wrapper over lysc cdata with type member"""

    @property
    def type(self):
        """Statements compiled type"""

        return self._context.sf.wrap(self._cdata.type)


class SCWrapperHasSp(WrapperBase):
    """Mixin for wrapper over lysc cdata with sp member"""

    @property
    def parsed(self):
        """Simply parsed version of this statement"""
        return self._context.sf.wrap(self._cdata.sp)


class SCWrapperHasParent(WrapperBase):
    """Mixin for wrapper over lysc cdata with parent member"""

    @property
    def parent(self):
        return self._context.sf.wrap(self._cdata.parent)


class SCWrapperHasRange(WrapperBase):
    """Mixin for wrapper over lysc cdata with range member"""

    @property
    def range(self) -> Union["SCRangeSigned", "SCRangeUnsigned"]:
        if self._cdata.basetype < SCType.DEC64:
            return self._context.sf.wrap(self._cdata.range, "lysc_range_signed")
        else:
            return self._context.sf.wrap(self._cdata.range, "lysc_range_unsigned")


class SCWrapperHasLength(WrapperBase):
    """Mixin for wrapper over lysc cdata with length member"""

    @property
    def length(self) -> Union["SCRangeSigned", "SCRangeUnsigned"]:
        if self._cdata.basetype < SCType.DEC64:
            return self._context.sf.wrap(self._cdata.length, "lysc_range_signed")
        else:
            return self._context.sf.wrap(self._cdata.length, "lysc_range_unsigned")


class SCWrapperHasRequireInstance(WrapperBase):
    """Mixin for wrapper over lysc cdata with require_instance member"""

    @property
    def require_instance(self) -> bool:
        return bool(self._cdata.require_instance)


class SCWrapperHasDflt(WrapperBase):
    """Mixin for wrapper over lysc cdata with dflt and dflt_mod members"""

    @property
    def default(self) -> str:
        try:
            return self._context.sf.wrap(self._cdata.dflt)
        except TypeError:
            # value is of type lyd_value
            return self._context.sf.wrap(self._cdata.dflt.original)

    @property
    def default_origin(self) -> "SModule":
        return self._context.sf.wrap(self._cdata.dflt_mod)


class SCWrapperHasWhen(WrapperBase):
    """Mixin for wrappers over lysc scdata with when member representing
       sized array of when statements"""

    def whens(self) -> Iterator["SCWhen"]:
        return self._context.sf.arr2gen(self._cdata.when)


@SchemaFactory.register_type_factory("struct lysc_module")
class SCModule(
    SCWrapperHasExts, SCWrapperHasNotifs,
):
    """Representation of compiled schema module instance"""

    @property
    def module(self) -> "SModule":
        """Corresponding schema module"""

        return self._context.sf.wrap(self._cdata.mod)

    def imports(self) -> Iterator["SCImport"]:
        """Imported modules"""

        return self._context.sf.arr2gen(self._cdata.imports)

    def rpcs(self) -> Iterator["SCRpc"]:
        """Modules Remote procedure calls"""

        return self._context.sf.arr2gen(self._cdata.rpcs, "lysc_rpc")

    def childs(
        self,
        intonpcont: bool = False,
        nochoice: bool = False,
        output: bool = False,
        withcase: bool = False,
        withchoice: bool = False,
    ) -> Iterator["SCNode"]:
        """Get modules top level nodes that can be instantiated in
        a data tree. Returned node can be from an augment"""

        opts = ored_options(
            intonpcont, nochoice, output, withcase, withchoice
        )
        next_node = lib.lys_getnext(ffi.NULL, ffi.NULL, self._cdata, opts)
        while next_node:
            yield self.context.sf.wrap(next_node)
            next_node = lib.lys_getnext(next_node, ffi.NULL, self._cdata, opts)

    __iter__ = childs


@SchemaFactory.register_type_factory("struct lysc_import")
class SCImport(
    SWrapperHasModule, SCWrapperHasExts,
):
    """Compiled import instance"""

    @property
    def prefix(self) -> str:
        return self._context.sf.wrap(self._cdata.prefix)


@SchemaFactory.register_type_factory("struct lysc_ident")
class SCIdentity(
    SWrapperHasName,
    SWrapperHasDesRef,
    SWrapperHasModule,
    SCWrapperHasExts,
    SWrapperHasStatus,
):
    """Representation of compiled identity statement"""

    def derived_identities(self) -> Iterator["SCIdentity"]:
        """Return generator that yields identities derived off this identity"""
        return self._context.sf.arr2gen(self._cdata.derived)


@SchemaFactory.register_subtyped_type_factory("create_node", "struct lysc_node")
class SCNode(
    SWrapperHasModule,
    SCWrapperHasParent,
    SWrapperHasName,
    SWrapperHasDesRef,
    SCWrapperHasExts,
):
    """Representation of compiled YANG data node"""

    @property
    def keyword(self) -> str:
        return Node.KEYWORDS.get(self._cdata.nodetype, "unknown")

    factories = {}
    realtypes = {}

    @classmethod
    def add_factory(cls, node_type, realtype):
        def _decor(scnode_factory):
            cls.factories[node_type] = scnode_factory
            cls.realtypes[node_type] = realtype
            return scnode_factory

        return _decor

    @classmethod
    def create_node(cls, cdata, context):
        casted = ffi.cast(cls.realtypes[cdata.nodetype], cdata)
        factory = cls.factories[cdata.nodetype]
        return factory(casted, context)

@SchemaFactory.register_type_factory("struct lysc_node_action_inout")
@SCNode.add_factory(Node.INPUT, "struct lysc_node *")
@SCNode.add_factory(Node.OUTPUT, "struct lysc_node *")
class SCInout(
    SCNode, SCWrapperHasChild, SCWrapperHasMusts
):
    pass

@SchemaFactory.register_type_factory("struct lysc_node_action")
@SCNode.add_factory(Node.ACTION, "struct lysc_node *")
class SCAction(
    SCNode, SWrapperHasStatus,
):
    def input_extension_instances(self) -> Iterator["SCExtensionInstance"]:
        return self._context.sf.wrap(self._cdata.input_exts)

    def output_extension_instances(self) -> Iterator["SCExtensionInstance"]:
        return self._context.sf.arr2gen(self._cdata.output_exts)

    @property
    def input(self) -> "SCInout":
        return self._context.sf.arr2gen(self._cdata.input)

    @property
    def output(self) -> "SCInout":
        return self._context.sf.wrap(self._cdata.output)


@SchemaFactory.register_named_type_factory("lysc_rpc")
@SCNode.add_factory(Node.RPC, "struct lysc_node *")
class SCRpc(SCAction):
    pass


@SchemaFactory.register_type_factory("struct lysc_node_notif")
@SCNode.add_factory(Node.NOTIFICATION, "struct lysc_node *")
class SCNotification(
    SCNode, SCWrapperHasData, SCWrapperHasMusts, SWrapperHasStatus,
):
    pass


@SchemaFactory.register_type_factory("struct lysc_node_container")
@SCNode.add_factory(Node.CONTAINER, "struct lysc_node_container *")
class SCContainer(
    SCNode,
    SCWrapperHasChild,
    SCWrapperHasMusts,
    SCWrapperHasActions,
    SWrapperHasStatus,
    SWrapperHasConfig,
    SCWrapperHasNotifs,
    SCWrapperHasWhen,
):
    # TODO LYS_MAND...
    pass


@SchemaFactory.register_type_factory("struct lysc_node_case")
@SCNode.add_factory(Node.CASE, "struct lysc_node_case *")
class SCCase(
    SCNode, SCWrapperHasChild, SCWrapperHasWhen,
):
    # TODO LYS_MAND...
    pass


@SchemaFactory.register_type_factory("struct lysc_node_choice")
@SCNode.add_factory(Node.CHOICE, "struct lysc_node_choice *")
class SCChoice(
    SCNode, SCWrapperHasCases, SCWrapperHasWhen,
):
    def cases(self) -> Iterator["SCCase"]:
        return self._context.sf.arr2gen(self._cdata.cases)

    # TODO LYS_MAND...
    @property
    def default(self) -> SCCase:
        return self._context.sf.wrap(self._cdata.dflt)


@SchemaFactory.register_type_factory("struct lysc_node_leaf")
@SCNode.add_factory(Node.LEAF, "struct lysc_node_leaf *")
class SCLeaf(
    SCNode, SCWrapperHasMusts, SCWrapperHasType, SWrapperHasUnits, SCWrapperHasWhen
):
    # TODO dflts
    pass


@SchemaFactory.register_type_factory("struct lysc_node_leaflist")
@SCNode.add_factory(Node.LEAFLIST, "struct lysc_node_leaflist *")
class SCLeafList(
    SCLeaf, SCWrapperHasMinMax, SWrapperHasConfig,
):
    pass


@SchemaFactory.register_type_factory("struct lysc_node_list")
@SCNode.add_factory(Node.LIST, "struct lysc_node_list *")
class SCList(
    SCNode,
    SCWrapperHasChild,
    SCWrapperHasMusts,
    SCWrapperHasActions,
    SCWrapperHasNotifs,
    SCWrapperHasMinMax,
    SCWrapperHasWhen,
):
    pass


@SchemaFactory.register_type_factory("struct lysc_node_anydata")
@SCNode.add_factory(Node.ANYDATA, "struct lysc_node_anydata *")
class SCAnydata(
    SCNode, SCWrapperHasMusts, SCWrapperHasWhen,
):
    pass


@SCNode.add_factory(Node.ANYXML, "struct lysc_node_anydata")
class SCAnyxml(SCAnydata):
    pass


@SchemaFactory.register_type_factory("struct lysc_ext_instance")
class SCExtensionInstance(
    SWrapperHasModule, SCWrapperHasExts,
):
    @property
    def definition(self) -> "SCExtension":
        """Get compiled extension definition"""
        return self._context.sf.wrap(getattr(self._cdata, "def"))

    @property
    def argument(self) -> str:
        """Get extension argument value"""
        return self._context.sf.wrap(self._cdata.argument)


@SchemaFactory.register_type_factory("struct lysc_iffeature")
class SCIffeature(WrapperBase):
    pass


@SchemaFactory.register_type_factory("struct lysc_when")
class SCWhen(
    SWrapperHasDesRef, SCWrapperHasExts, SWrapperHasStatus,
):
    pass


@SchemaFactory.register_type_factory("struct lysc_must")
class SCMust(
    SWrapperHasDesRef, SWrapperHasEmsgEpptag, SCWrapperHasExts,
):
    # todo condition and prefixes...
    pass


@SchemaFactory.register_type_factory("struct lysc_ext")
class SCExtension(
    SWrapperHasName, SWrapperHasArgument, SCWrapperHasExts, SWrapperHasModule
):
    pass


@SchemaFactory.register_subtyped_type_factory("create_type", "struct lysc_type")
class SCType(
    SCWrapperHasExts,
):

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
        BOOL: "bool",
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

    factories = {}
    realtypes = {}

    @classmethod
    def add_factory(cls, type_base, realtype):
        def _decor(type_factory):
            cls.factories[type_base] = type_factory
            cls.realtypes[type_base] = realtype
            return type_factory

        return _decor

    @classmethod
    def create_type(cls, cdata, context):
        factory = cls.factories[cdata.basetype]
        return factory(cdata, context)


@SCType.add_factory(SCType.UINT8, "struct lysc_type_num *")
@SCType.add_factory(SCType.UINT16, "struct lysc_type_num *")
@SCType.add_factory(SCType.UINT32, "struct lysc_type_num *")
@SCType.add_factory(SCType.UINT64, "struct lysc_type_num *")
@SCType.add_factory(SCType.INT8, "struct lysc_type_num *")
@SCType.add_factory(SCType.INT16, "struct lysc_type_num *")
@SCType.add_factory(SCType.INT32, "struct lysc_type_num *")
@SCType.add_factory(SCType.INT64, "struct lysc_type_num *")
@SchemaFactory.register_type_factory("struct lysc_type_num")
class SCTypeNumeric(
    SCType, SCWrapperHasRange,
):
    pass


@SCType.add_factory(SCType.DEC64, "struct lysc_type_dec *")
@SchemaFactory.register_type_factory("struct lysc_type_dec")
class SCTypeDec64(SCTypeNumeric,):
    @property
    def fraction_digits(self) -> int:
        return self._cdata.fraction_digits


@SCType.add_factory(SCType.STRING, "struct lysc_type_str *")
@SchemaFactory.register_type_factory("struct lysc_type_str")
class SCTypeString(
    SCType, SCWrapperHasLength,
):
    def patterns(self) -> Iterator["SCPattern"]:
        return self._context.sf.arr2gen(self._cdata.patterns)


@SCType.add_factory(SCType.ENUM, "struct lysc_type_enum *")
@SchemaFactory.register_type_factory("struct lysc_type_enum")
class SCTypeEnum(SCType):
    def enums(self) -> Iterator["SCEnumItem"]:
        return self._context.sf.arr2gen(self._cdata.enums, "lysc_enumitem")


@SCType.add_factory(SCType.BITS, "struct lysc_type_bits *")
@SchemaFactory.register_type_factory("struct lysc_type_bits")
class SCTypeBits(SCType):
    def bits(self) -> Iterator["SCBitItem"]:
        return self._context.sf.arr2gen(self._cdata.bits, "lysc_bititem")


@SCType.add_factory(SCType.LEAFREF, "struct lysc_type_leafref *")
@SchemaFactory.register_type_factory("struct lysc_type_leafref")
class SCTypeLeafref(
    SCType, SCWrapperHasRequireInstance,
):
    @property
    def realtype(self) -> SCType:
        return self._context.sf.wrap(self._cdata.realtype)


@SCType.add_factory(SCType.IDENT, "struct lysc_type_identityref *")
@SchemaFactory.register_type_factory("struct lysc_type_identityref")
class SCTypeIdentityref(SCType,):
    def bases(self) -> Iterator["SCSCIdentity"]:
        return self._context.sf.arr2gen(self._cdata.bases)


@SCType.add_factory(SCType.INST, "struct lysc_type_instanceid *")
@SchemaFactory.register_type_factory("struct lysc_type_instanceid")
class SCTypeInstanceid(
    SCType, SCWrapperHasRequireInstance,
):
    pass


@SCType.add_factory(SCType.UNION, "struct lysc_type_union *")
@SchemaFactory.register_type_factory("struct lysc_type_union")
class SCTypeUnion(SCType,):
    def types(self) -> Iterator["SCType"]:
        return self._context.sf.arr2gen(self._cdata.types)


@SCType.add_factory(SCType.BINARY, "struct lysc_type_bin *")
@SchemaFactory.register_type_factory("struct lysc_type_bin")
class SCTypeBinary(
    SCType, SCWrapperHasLength,
):
    pass


@SCType.add_factory(SCType.UNKNOWN, "struct lysc_type *")
class SCTypeUnknown(SCType):
    pass


@SCType.add_factory(SCType.BOOL, "struct lysc_type *")
class SCTypeBool(SCType):
    pass


@SCType.add_factory(SCType.EMPTY, "struct lysc_type *")
class SCTypeEmpty(SCType):
    pass


class SCRangeBase(
    SWrapperHasDesRef, SWrapperHasEmsgEpptag, SCWrapperHasExts,
):
    pass


@SchemaFactory.register_named_type_factory("lysc_range_signed")
class SCRangeSigned(SCRangeBase):
    @property
    def min(self) -> Union[int, None]:
        if self._cdata.parts:
            return self._cdata.parts.min_64
        else:
            return None

    @property
    def max(self) -> Union[int, None]:
        if self._cdata.parts:
            return self._cdata.parts.max_64
        else:
            return None


@SchemaFactory.register_named_type_factory("lysc_range_unsigned")
class SCRangeUnsigned(SCRangeBase):
    @property
    def min(self) -> Union[int, None]:
        if self._cdata.parts:
            return self._cdata.parts.min_u64
        else:
            return None

    @property
    def max(self) -> Union[int, None]:
        if self._cdata.parts:
            return self._cdata.parts.max_u64
        else:
            return None


@SchemaFactory.register_type_factory("struct lysc_pattern")
class SCPattern(
    SWrapperHasDesRef, SWrapperHasEmsgEpptag, SCWrapperHasExts,
):
    @property
    def regexp(self) -> Tuple[str, bool]:
        """Get patterns regular expression and invert-match value"""
        inverted = self._cdata.expr[0] == b"\x15"
        return self._context.sf.wrap(self._cdata.expr + 1), inverted


@SchemaFactory.register_type_factory("struct lysc_type_bitenum_item")
class SCBitEnumItemBase(
    SWrapperHasName,
    SWrapperHasDesRef,
    SCWrapperHasExts,
    SWrapperHasStatus,
):
    pass


@SchemaFactory.register_named_type_factory("lysc_bititem")
class SCBitItem(SCBitEnumItemBase):
    @property
    def position(self) -> Union[int, None]:
        if self._cdata.flags & lib.LYS_SET_VALUE:
            return self._cdata.position
        else:
            return None


@SchemaFactory.register_named_type_factory("lysc_enumitem")
class SCEnumItem(SCBitEnumItemBase):
    @property
    def value(self) -> Union[int, None]:
        if self._cdata.flags & lib.LYS_SET_VALUE:
            return self._cdata.value
        else:
            return None
