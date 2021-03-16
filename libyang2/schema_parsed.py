# Copyright (c) 2020 CESNET, z.s.p.o.
# SPDX-License-Identifier: BSD-3-Clause
# Author David Sedlák

from typing import Union, Iterator, TYPE_CHECKING, Tuple

from _libyang import lib, ffi
from libyang2.schema_compiled import SCType

from .utils import Node, SchemaFactory, WrapperBase
from .schema import (
    SWrapperHasName,
    SWrapperHasDesRef,
    SWrapperHasStatus,
    SWrapperHasConfig,
    SWrapperHasUnits,
    SWrapperHasEmsgEpptag,
    SWrapperHasArgument,
)

if TYPE_CHECKING:
    from .schema_compiled import SCExtension, SCExtensionInstance


class SPWrapperHasMinMax(WrapperBase):
    """Mixin for wrappers over lysp cdata with min and max members

    Provides min and max getters
    """

    @property
    def min(self) -> int:
        """Get min value"""

        if self._cdata.flags & lib.LYS_SET_MIN:
            return self._cdata.min
        else:
            return None

    @property
    def max(self) -> int:
        """Get max value"""

        if self._cdata.flags & lib.LYS_SET_MAX:
            return self._cdata.max
        else:
            return None


class SPWrapperHasRev(WrapperBase):
    """Mixin for wrappers over lysp cdata with revision member

    Provides revision getter
    """

    @property
    def revision(self) -> Union[None, str]:
        """Get revision"""

        rev = self._context.sf.wrap(self._cdata.rev)
        if not rev:
            return None
        else:
            return rev


class SPWrapperHasIffeatures(WrapperBase):
    """Mixin for wrappers over lysp cdata with iffeatures member

    Provides revision getter.
    """

    # TODO check conflicting types due to some changes of char *** to lysp_qname ** in lysp_feature
    def iffeatures(self) -> Iterator[str]:
        """Get revisions, returned value is generator"""

        return self._context.sf.arr2gen(self._cdata.iffeatures)


class SPWrapperHasBases(WrapperBase):
    """Mixin for wrappers over lysp cdata with bases member

    Provides bases getter.
    """

    def bases(self) -> Iterator[str]:
        """Get bases, returned value is generator"""

        return self._context.sf.arr2gen(self._cdata.bases)


class SPWrapperHasExts(WrapperBase):
    """Mixin for wrappers over lysp cdata with exts member

    Provides extension_instances getter.
    """

    def extension_instances(self) -> Iterator["SPExtensionInstance"]:
        """Get extension instances, returned value is generator"""

        return self._context.sf.arr2gen(self._cdata.exts)


class SPWrapperHasType(WrapperBase):
    """Mixin for wrappers over lysp cdata with type member

    Provides type getter.
    """

    @property
    def type(self) -> "SPType":
        """Get type"""
        return self._context.sf.wrap(self._cdata.type)


class SPWrapperHasDflts(WrapperBase):
    """Mixin for wrappers over lysp cdata with dflts member.

    Provides defaults getter.
    """

    def defaults(self) -> Iterator[str]:
        """Get default values.

        Returned value is generator that yields all default values.
        """

        return self._context.sf.arr2gen(self._cdata.dflts)


class SPWrapperHasDflt(WrapperBase):
    """Mixin for wrappers over lysp cdata with dflt member.

    Provides default getter.
    """

    @property
    def default(self) -> str:
        # TODO reflect char * -> lysp_qname change
        return self._context.sf.wrap(self._cdata.dflt)


class SPWrapperHasGroupings(WrapperBase):
    """Mixin for wrappers over lysp cdata with groupings member.

    Provides groupings getter.
    """

    def groupings(self) -> Iterator["SPGrouping"]:
        return self._context.sf.arr2gen(self._cdata.groupings)


class SPWrapperHasTypedefs(WrapperBase):
    """Mixin for wrappers over lysp cdata with typedefs member.

    Provides typedefs getter.
    """

    def typedefs(self) -> Iterator["SPTypedef"]:
        return self._context.sf.arr2gen(self._cdata.typedefs)


class SPWrapperHasData(WrapperBase):
    """Mixin for wrappers over lysp cdata with data member.

    Provides childs getter.
    """

    def childs(self) -> Iterator["SPNode"]:
        return self._context.sf.ll2gen(self._cdata.data, "next")

    __iter__ = childs


class SPWrapperHasChild(WrapperBase):
    """Mixin for wrappers over lysp cdata with child member.

    Provides child getter.
    """

    def childs(self) -> Iterator["SPNode"]:
        return self._context.sf.ll2gen(self._cdata.child, "next")

    __iter__ = childs


class SPWrapperHasParent(WrapperBase):
    """Mixin for wrappers over lysp cdata with parent member.

    Provides parent getter.
    """

    @property
    def parent(self):
        return self._context.sf.wrap(self._cdata.parent)


class SPWrapperHasActions(WrapperBase):
    """Mixin for wrappers over lysp cdata with actions member.

    Provides actions getter.
    """

    def actions(self) -> Iterator["SPAction"]:
        return self._context.sf.arr2gen(self._cdata.actions)


class SPWrapperHasNotifs(WrapperBase):
    """Mixin for wrappers over lysp cdata with actions member.

    Provides actions getter.
    """

    def notifications(self) -> Iterator["SPNotification"]:
        return self._context.sf.arr2gen(self._cdata.notifs)


class SPWrapperHasNodeid(WrapperBase):
    """Mixin for wrappers over lysp cdata with nodeid member.

    Provides nodeid getter.
    """

    @property
    def nodeid(self) -> str:
        return self._context.sf.wrap(self._cdata.nodeid)


class SPWrapperHasWhen(WrapperBase):
    """Mixin for wrappers over lysp cdata with when member.

    Provides when getter.
    """

    @property
    def when(self) -> "SPWhen":
        return self._context.sf.wrap(self._cdata.when)


class SPWrapperHasInput(WrapperBase):
    """Mixin for wrappers over lysp cdata with input member.

    Provides input getter.
    """

    @property
    def input(self) -> "SPInputOutput":
        return self._context.sf.wrap(self._cdata.input)


class SPWrapperHasOutput(WrapperBase):
    """Mixin for wrappers over lysp cdata with output member.

    Provides output getter.
    """

    @property
    def output(self) -> "SPInputOutput":
        return self._context.sf.wrap(self._cdata.output)


class SPWrapperHasMusts(WrapperBase):
    """Mixin for wrappers over lysp cdata with musts member.

    Provides musts getter.
    """

    def musts(self) -> Iterator["SPRestriction"]:
        return self._context.sf.arr2gen(self._cdata.musts)


class SPWrapperHasUniques(WrapperBase):
    """Mixin for wrappers over lysp cdata with uniques member.

    Provides unique_specifications getter.
    """

    def unique_specifications(self) -> Iterator[str]:
        # TODO reflect change from string to lysp_qname in all subclasses ...
        return self._context.sf.arr2gen(self._cdata.uniques)


class SPWrapperHasPresence(WrapperBase):
    """Mixin for wrappers over lysp cdata with presence member.

    Provides presence getter.
    """

    @property
    def presence(self) -> str:
        return self._context.sf.wrap(self._cdata.presence)


class SPWrapperHasAugments(WrapperBase):
    """Mixin for wrappers over lysp cdata with augments member.

    Provides augments getter.
    """

    def augments(self) -> Iterator["SPAugment"]:
        return self._context.sf.arr2gen(self._cdata.augments)


class SPWrapperHasExtensions(WrapperBase):
    """Mixin for wrappers over lysp cdata with extensions member.

    Provides extensions getter.
    """

    def extensions(self) -> Iterator["SPExtension"]:
        return self._context.sf.arr2gen(self._cdata.extensions)


class SPWrapperHasMandatory(WrapperBase):
    """Mixin for wrappers over lysp cdata with available mandatory flag.

    Provides mandatory getter.
    """

    @property
    def mandatory(self) -> Union[bool, None]:
        if self._cdata.flags & lib.LYS_MAND_TRUE:
            return True
        elif self._cdata.flags & lib.LYS_MAND_FALSE:
            return False
        else:
            return None


class SPWrapperHasPrefix(WrapperBase):
    """Mixin for wrappers over lysp cdata with available prefix member.

    Provides prefix getter.
    """

    @property
    def prefix(self) -> str:
        return self._context.sf.wrap(self._cdata.prefix)


@SchemaFactory.register_type_factory("struct lysp_module")
class SPModule(
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasData,
    SPWrapperHasAugments,
    SPWrapperHasNotifs,
    SPWrapperHasExts,
):
    """Representation of parsed module"""

    @property
    def module(self) -> "SModule":
        return self._context.sf.wrap(self._cdata.mod)

    @property
    def version(self) -> str:
        """Module's version"""

        if self._cdata.version & lib.LYS_VERSION_1_1:
            return "YANG 1.1"
        else:
            return "YANG 1.0"

    def revisions(self) -> Iterator["SPRevision"]:
        return self._context.sf.arr2gen(self._cdata.revs)

    def imports(self) -> Iterator["SPImport"]:
        return self._context.sf.arr2gen(self._cdata.imports)

    def includes(self) -> Iterator["SPInclude"]:
        return self._context.sf.arr2gen(self._cdata.includes)

    def extensions(self) -> Iterator["SPExtension"]:
        return self._context.sf.arr2gen(self._cdata.extensions)

    def features(self) -> Iterator["SPFeature"]:
        return self._context.sf.arr2gen(self._cdata.features)

    def identities(self) -> Iterator["SPIdentity"]:
        return self._context.sf.arr2gen(self._cdata.identities)

    def rpcs(self) -> Iterator["SPRpc"]:
        return self._context.sf.arr2gen(self._cdata.rpcs, "rpc")

    def deviations(self) -> Iterator["SPDeviation"]:
        return self._context.sf.arr2gen(self._cdata.deviations)


@SchemaFactory.register_type_factory("struct lysp_submodule")
class SPSubmodule(
    SPModule, SWrapperHasName, SWrapperHasDesRef, SPWrapperHasPrefix
):
    """Representation of parsed submodule"""

    @property
    def belongsto(self) -> str:
        # todo maybe change name of this property This was changed from belongsto to mod in latest libyang2
        return self._context.sf.wrap(self._cdata.mod)

    @property
    def filepath(self) -> Union[str, None]:
        return self._context.sf.wrap(self._cdata.filepath)

    @property
    def organization(self) -> Union[str, None]:
        return self._context.sf.wrap(self._cdata.org)

    @property
    def contact(self) -> Union[str, None]:
        return self._context.sf.wrap(self._cdata.contact)

    @property
    def version(self) -> str:
        if self._cdata.version & lib.LYS_VERSION_1_1:
            return "YANG 1.1"
        else:
            return "YANG 1.0"


@SchemaFactory.register_type_factory("struct lysp_qname")
class SPQualifiedName(WrapperBase):
    """Representation of qualified name."""

    def name(self):
        return self._context.sf.wrap(self._cdata.str)

    def module(self):
        return self._context.sf.wrap(self._cdata.mod)

    __str__ = name


@SchemaFactory.register_type_factory("struct lysp_revision")
class SPRevision(
    SWrapperHasDesRef, SPWrapperHasExts,
):
    """Representation of parsed revision"""

    @property
    def date(self) -> Union[str, None]:
        dt = self._context.sf.wrap(self._cdata.date)
        if not dt:
            return None
        else:
            return dt


@SchemaFactory.register_type_factory("struct lysp_import")
class SPImport(
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasExts,
    SPWrapperHasRev,
    SPWrapperHasPrefix,
):
    """Representation of parsed import"""

    @property
    def module(self) -> "SModule":
        return self._context.sf.wrap(self._cdata.module)


@SchemaFactory.register_type_factory("struct lysp_include")
class SPInclude(
    SWrapperHasName, SWrapperHasDesRef, SPWrapperHasExts, SPWrapperHasRev,
):
    """Representation of parsed include"""

    @property
    def submodule(self) -> SPSubmodule:
        return self._context.sf.wrap(self._cdata.submodule)


@SchemaFactory.register_type_factory("struct lysp_ext")
class SPExtension(
    SWrapperHasName,
    SWrapperHasArgument,
    SWrapperHasDesRef,
    SPWrapperHasExts,
    SWrapperHasStatus,
):
    """Representation of parsed extension"""

    @property
    def compiled(self) -> "SCExtension":
        return self._context.sf.wrap(self._cdata.compiled)


@SchemaFactory.register_type_factory("struct lysp_ext_instance")
class SPExtensionInstance(
    SWrapperHasName, SWrapperHasArgument, SPWrapperHasChild,
):
    """Representation of parsed extension instance"""

    @property
    def is_from_yin(self) -> bool:
        return bool(self._cdata.yin & lib.LYS_YIN)

    @property
    def compiled(self) -> "SCExtensionInstance":
        return self._context.sf.wrap(self._cdata.compiled)


@SchemaFactory.register_type_factory("struct lysp_stmt")
class SPStatementGeneric(WrapperBase):
    """Representation of parsed generic substatement from extension instance"""

    def __iter__(self):
        return self._context.sf.ll2gen(self._cdata.next, "next")

    @property
    def statement(self) -> str:
        return self._context.sf.wrap(self._cdata.stmt)

    @property
    def argument(self) -> str:
        return self._context.sf.wrap(self._cdata.arg)

    @property
    def possible_yin_attribute(self) -> bool:
        return bool(self._cdata.flags & lib.LYS_YIN_ATTR)

    def childs(self) -> Iterator["SPStatementGeneric"]:
        return self._context.sf.ll2gen(self._cdata.child, "child")


@SchemaFactory.register_type_factory("struct lysp_feature")
class SPFeature(
    SWrapperHasName,
    SPWrapperHasIffeatures,
    SWrapperHasDesRef,
    SPWrapperHasExts,
    SWrapperHasStatus,
):
    """Representation of parsed feature."""

    pass


@SchemaFactory.register_type_factory("struct lysp_ident")
class SPIdentity(
    SWrapperHasName,
    SPWrapperHasIffeatures,
    SPWrapperHasBases,
    SWrapperHasDesRef,
    SPWrapperHasExts,
    SWrapperHasStatus,
):
    """Representation of parsed identity."""

    pass


@SchemaFactory.register_type_factory("struct lysp_tpdf")
class SPTypedef(
    SWrapperHasName,
    SWrapperHasUnits,
    SPWrapperHasDflt,
    SWrapperHasDesRef,
    SPWrapperHasExts,
    SPWrapperHasType,
    SWrapperHasStatus,
):
    """Representation of parsed typedef."""

    pass


@SchemaFactory.register_type_factory("struct lysp_deviation")
class SPDeviation(SPWrapperHasNodeid, SWrapperHasDesRef, SPWrapperHasExts):
    """Representation of parsed deviation."""

    def deviates(self) -> Iterator["SPDeviate"]:
        return self._context.sf.ll2gen(self._cdata.deviates)


@SchemaFactory.register_type_factory("struct lysp_type")
class SPType(
    SWrapperHasName,
    SPWrapperHasBases,
    SPWrapperHasExts,
    SWrapperHasConfig,
    SWrapperHasStatus,
):
    """Representation of parsed type."""

    @property
    def range(self) -> Union["SPRestriction", None]:
        return self._context.sf.wrap(self._cdata.range)

    @property
    def length(self) -> Union["SPRestriction", None]:
        return self._context.sf.wrap(self._cdata.length)

    def patterns(self) -> Iterator["SPRestriction"]:
        return self._context.sf.arr2gen(self._cdata.patterns, "lysp_pattern")

    def enums(self) -> Iterator["SPEnum"]:
        return self._context.sf.arr2gen(self._cdata.enums, "enum")

    def bits(self) -> Iterator["SPBit"]:
        return self._context.sf.arr2gen(self._cdata.bits, "bit")

    def types(self) -> Iterator["SPType"]:
        return self._context.sf.arr2gen(self._cdata.types)

    @property
    def fraction_digits(self) -> int:
        return self._cdata.fraction_digits

    @property
    def require_instance(self) -> bool:
        return bool(self._cdata.flags & lib.LYS_SET_REQINST)

    @property
    def compiled(self) -> Union["SCType", None]:
        return self._context.sf.wrap(self._cdata.compiled)


@SchemaFactory.register_type_factory("struct lysp_when")
class SPWhen(
    SWrapperHasDesRef, SPWrapperHasExts,
):
    """Representation of parsed when."""

    @property
    def condition(self) -> str:
        return self._context.sf.wrap(self._cdata.cond)


@SchemaFactory.register_type_factory("struct lysp_restr")
class SPRestriction(
    SWrapperHasDesRef, SPWrapperHasExts, SWrapperHasEmsgEpptag,
):
    """Representation of parsed restriction."""

    @property
    def argument(self) -> str:
        # TODO reflect change from char * to lysp_qname in arg member
        return self._context.sf.wrap(self._cdata.arg)


@SchemaFactory.register_named_type_factory("lysp_pattern")
class SPPattern(SPRestriction):
    """Representation of parsed pattern."""

    @property
    def argument(self) -> Tuple[str, bool]:
        arg = self._cdata.arg
        inverted = arg[0] == b"\x15"
        return self._context.sf.wrap(arg + 1), inverted


@SchemaFactory.register_subtyped_type_factory("create_deviate", "struct lysp_deviate")
class SPDeviate(SPWrapperHasExts):
    """Base class for deviate types."""

    def __iter__(self):
        return self._context.sf.ll2gen(self._cdata.next, "next")

    factories = {}
    realtypes = {}

    @classmethod
    def add_factory(cls, deviate_type, realtype):
        def _decor(deviate_factory):
            cls.factories[deviate_type] = deviate_factory
            cls.realtypes[deviate_type] = realtype
            return deviate_factory

        return _decor

    @classmethod
    def create_deviate(cls, cdata, context):
        casted = ffi.cast(cls.realtypes[cdata.mod], cdata)
        factory = cls.factories[cdata.mod]
        return factory(casted, context)


@SPDeviate.add_factory(lib.LYS_DEV_NOT_SUPPORTED, "struct lysp_deviate *")
class SPDeviateNotSupported(SPDeviate):
    """Representation of parsed deviate not supported."""

    pass


@SchemaFactory.register_type_factory("struct lysp_deviate_del")
@SPDeviate.add_factory(lib.LYS_DEV_DELETE, "struct lysp_deviate_del *")
class SPDeviateDelete(
    SPDeviate,
    SWrapperHasUnits,
    SPWrapperHasMusts,
    SPWrapperHasDflts,
    SPWrapperHasUniques,
):
    """Representation of parsed deviate delete."""

    pass


@SchemaFactory.register_type_factory("struct lysp_deviate_add")
@SPDeviate.add_factory(lib.LYS_DEV_ADD, "struct lysp_deviate_add *")
class SPDeaviateAdd(
    SPDeviateDelete,
    SPWrapperHasMinMax,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SPWrapperHasMandatory,
):
    """Representation of parsed deviate add."""

    pass


@SchemaFactory.register_type_factory("struct lysp_deviate_rpl")
@SPDeviate.add_factory(lib.LYS_DEV_REPLACE, "struct lysp_deviate_rpl *")
class SPDeviateReplace(
    SPDeviate,
    SPWrapperHasType,
    SWrapperHasUnits,
    SPWrapperHasDflt,
    SPWrapperHasMinMax,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SPWrapperHasMandatory,
):
    """Representation of parsed deviate replace."""

    pass


class SPEnumBitBase(
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasIffeatures,
    SPWrapperHasExts,
    SWrapperHasStatus,
):
    """Base class for enum and bit types"""

    pass


@SchemaFactory.register_named_type_factory("enum")
@SchemaFactory.register_type_factory("struct lysp_type_enum")
class SPEnum(SPEnumBitBase):
    """Representation of parsed enum."""

    @property
    def value(self) -> Union[int, None]:
        if self._cdata.flags & lib.LYS_SET_VALUE:
            return self._cdata.value
        else:
            return None


@SchemaFactory.register_named_type_factory("bit")
class SPBit(SPEnumBitBase):
    """Representation of parsed bit."""

    @property
    def position(self) -> Union[int, None]:
        if self._cdata.flags & lib.LYS_SET_VALUE:
            return self._cdata.value
        else:
            return None

@SchemaFactory.register_subtyped_type_factory("create_node", "struct lysp_node")
class SPNode(
    SPWrapperHasParent, SPWrapperHasExts,
):
    """Base class for schema node types."""

    @property
    def keyword(self) -> str:
        return Node.KEYWORDS.get(self._cdata.nodetype, "unknown")

    factories = {}
    realtypes = {}

    @classmethod
    def add_factory(cls, node_type, realtype):
        def _decor(deviate_factory):
            cls.factories[node_type] = deviate_factory
            cls.realtypes[node_type] = realtype
            return deviate_factory

        return _decor

    @classmethod
    def create_node(cls, cdata, context):
        casted = ffi.cast(cls.realtypes[cdata.nodetype], cdata)
        factory = cls.factories[cdata.nodetype]
        return factory(casted, context)


@SPNode.add_factory(Node.UNKNOWN, "struct lysp_node *")
class SPNodeUnknown(
    SPNode, SWrapperHasName, SWrapperHasDesRef, SPWrapperHasWhen, SPWrapperHasIffeatures
):
    """Unknown node."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_container")
@SPNode.add_factory(Node.CONTAINER, "struct lysp_node_container *")
class SPContainer(
    SPNode,
    SPWrapperHasMusts,
    SPWrapperHasPresence,
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasChild,
    SPWrapperHasActions,
    SPWrapperHasNotifs,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasIffeatures,
    SPWrapperHasWhen,
):
    """Representation of parsed container."""

    pass


class SPLeafLeafListBase(
    SPNode,
    SPWrapperHasMusts,
    SPWrapperHasType,
    SWrapperHasUnits,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
):
    """Base class for leaf and leaf-list types."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_leaf")
@SPNode.add_factory(Node.LEAF, "struct lysp_node_leaf *")
class SPLeaf(
    SPLeafLeafListBase, SPWrapperHasDflt, SPWrapperHasWhen,
):
    """Representation of parsed leaf."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_leaflist")
@SPNode.add_factory(Node.LEAFLIST, "struct lysp_node_leaflist *")
class SPLeafList(
    SPLeafLeafListBase, SPWrapperHasDflts, SPWrapperHasMinMax, SPWrapperHasWhen,
):
    """Representation of parsed leaf-list."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_list")
@SPNode.add_factory(Node.LIST, "struct lysp_node_list *")
class SPList(
    SPNode,
    SPWrapperHasMusts,
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasChild,
    SPWrapperHasActions,
    SPWrapperHasNotifs,
    SPWrapperHasUniques,
    SPWrapperHasMinMax,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
):
    """Representation of parsed list."""

    @property
    def key(self) -> str:
        return self._context.sf.wrap(self._cdata.key)


@SchemaFactory.register_type_factory("struct lysp_node_choice")
@SPNode.add_factory(Node.CHOICE, "struct lysp_node_choice *")
class SPChoice(
    SPNode,
    SPWrapperHasChild,
    SPWrapperHasDflt,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SPWrapperHasMandatory,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
):
    """Representation of parsed choice."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_case")
@SPNode.add_factory(Node.CASE, "struct lysp_node_case *")
class SPCase(
    SPNode,
    SPWrapperHasChild,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
):
    """Representation of parsed case."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_anydata")
@SPNode.add_factory(Node.ANYDATA, "struct lysp_node_anydata *")
class SPAnydata(
    SPNode,
    SPWrapperHasMusts,
    SWrapperHasConfig,
    SWrapperHasStatus,
    SPWrapperHasMandatory,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
):
    """Representation of parsed anydata."""

    pass


@SPNode.add_factory(Node.ANYXML, "struct lysp_node_anydata *")
class SPAnyxml(SPAnydata):
    """Representation of parsed anyxml."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_uses")
@SPNode.add_factory(Node.USES, "struct lysp_node_uses *")
class SPUses(
    SPNode,
    SPWrapperHasAugments,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
):
    """Representation of parsed uses."""

    def refines(self) -> Iterator["SPRefine"]:
        return self._context.sf.arr2gen(self._cdata.refines)


@SchemaFactory.register_type_factory("struct lysp_node_action_inout")
@SPNode.add_factory(Node.INPUT, "struct lysp_node_action_inout *")
@SPNode.add_factory(Node.OUTPUT, "struct lysp_node_action_inout *")
class SPInputOutput(
    SPNode,
    SPWrapperHasMusts,
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasChild,
):
    """Representation of parsed input/output statement."""

    pass


@SchemaFactory.register_type_factory("struct lysp_refine")
class SPRefine(
    SPWrapperHasNodeid,
    SWrapperHasDesRef,
    SPWrapperHasIffeatures,
    SPWrapperHasMusts,
    SPWrapperHasPresence,
    SPWrapperHasDflts,
    SPWrapperHasMinMax,
    SPWrapperHasExts,
    SWrapperHasConfig,
    SPWrapperHasMandatory,
):
    """Representation of parsed refine."""

    pass


@SchemaFactory.register_named_type_factory("action")
@SchemaFactory.register_type_factory("struct lysp_node_action")
@SPNode.add_factory(Node.ACTION, "struct lysp_node_action *")
class SPAction(
    SPNode,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasIffeatures,
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasInput,
    SPWrapperHasOutput,
):
    """Representation of parsed action."""

    pass


@SchemaFactory.register_named_type_factory("rpc")
@SPNode.add_factory(Node.RPC, "struct lysp_node_action *")
class SPRpc(SPAction, SWrapperHasStatus):
    """Representation of parsed rpc."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_notif")
@SPNode.add_factory(Node.NOTIFICATION, "struct lysp_node_notif *")
class SPNotification(
    SPNode,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasIffeatures,
    SPWrapperHasMusts,
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasChild,
):
    """Representation of parsed notification."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_grp")
@SPNode.add_factory(Node.GROUPING, "struct lysp_node_grp *")
class SPGrouping(
    SPNode,
    SWrapperHasStatus,
    SWrapperHasName,
    SWrapperHasDesRef,
    SPWrapperHasTypedefs,
    SPWrapperHasGroupings,
    SPWrapperHasChild,
    SPWrapperHasActions,
    SPWrapperHasNotifs,
):
    """Representation of parsed grouping."""

    pass


@SchemaFactory.register_type_factory("struct lysp_node_augment")
@SPNode.add_factory(Node.AUGMENT, "struct lysp_node_augment *")
class SPAugment(
    SPNode,
    SWrapperHasStatus,
    SPWrapperHasChild,
    SPWrapperHasNodeid,
    SWrapperHasDesRef,
    SPWrapperHasWhen,
    SPWrapperHasIffeatures,
    SPWrapperHasActions,
    SPWrapperHasNotifs,
):
    """Representation of parsed augment."""

    pass
