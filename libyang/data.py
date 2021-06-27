# Copyright (c) 2020 6WIND S.A.
# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Union, Iterator, TextIO

from _libyang import ffi, lib
from .utils import SchemaFactory, Node, WrapperBase, str2c, c2str

if TYPE_CHECKING:
    from .schema_compiled import SCNode, SCExtension
    from .schema import SModule


def data_format(fmt_string: str) -> int:
    if fmt_string == "json":
        return lib.LYD_JSON
    if fmt_string == "xml":
        return lib.LYD_XML
    if fmt_string == "lyb":
        return lib.LYD_LYB

    raise ValueError(f"unknown data format: {fmt_string}")


def data_out_format(fmt_string: str) -> int:
    if fmt_string == "json":
        return lib.LYD_JSON
    if fmt_string == "xml":
        return lib.LYD_XML
    if fmt_string == "lyb":
        return lib.LYD_LYB

    raise ValueError("unknown data format: %r" % fmt_string)


def data_validation_options(
    validate_no_state: bool = False, validate_present: bool = False
) -> int:
    flags = 0
    if validate_no_state:
        flags |= lib.LYD_VALIDATE_NO_STATE
    if validate_present:
        flags |= lib.LYD_VALIDATE_PRESENT

    return flags


def data_duplication_options(
    duplicate_no_meta: bool = False,
    duplicate_resursive: bool = False,
    duplicate_wtih_flags: bool = False,
    duplicate_with_parent: bool = False,
):
    flags = 0
    if duplicate_no_meta:
        flags |= lib.LYD_DUP_NO_META
    if duplicate_resursive:
        flags |= lib.LYD_DUP_RECURSIVE
    if duplicate_wtih_flags:
        flags |= lib.LYD_DUP_WITH_FLAGS
    if duplicate_with_parent:
        flags |= lib.LYD_DUP_WITH_PARENTS

    return flags


def data_parser_options(
    parse_no_state: bool = False,
    parse_only: bool = False,
    parse_opaq: bool = False,
    parse_strict: bool = False,
    parse_lyb_mod_update: bool = False,
) -> int:
    flags = 0
    if parse_lyb_mod_update:
        flags |= lib.LYD_PARSE_LYB_MOD_UPDATE
    if parse_no_state:
        flags |= lib.LYD_PARSE_NO_STATE
    if parse_only:
        flags |= lib.LYD_PARSE_ONLY
    if parse_opaq:
        flags |= lib.LYD_PARSE_OPAQ
    if parse_strict:
        flags |= lib.LYD_PARSE_STRICT

    return flags


def data_printer_flags(
    keep_empty_cont: bool = False,
    wd_all: bool = False,
    wd_all_tag: bool = False,
    wd_explicit: bool = False,
    wd_impl_tag: bool = False,
    wd_mask: bool = False,
    wd_trim: bool = False,
    withsiblings: bool = False,
) -> int:
    flags = 0
    if keep_empty_cont:
        flags |= lib.LYD_PRINT_KEEPEMPTYCONT
    if wd_all:
        flags |= lib.LYD_PRINT_WD_ALL
    if wd_all_tag:
        flags |= lib.LYD_PRINT_WD_ALL_TAG
    if wd_explicit:
        flags |= lib.LYD_PRINT_WD_EXPLICIT
    if wd_impl_tag:
        flags |= lib.LYD_PRINT_WD_IMPL_TAG
    if wd_mask:
        flags |= lib.LYD_PRINT_WD_MASK
    if wd_trim:
        flags |= lib.LYD_PRINT_WD_TRIM
    if withsiblings:
        flags |= lib.LYD_PRINT_WITHSIBLINGS

    return flags


def data_merge_options(
    merge_defaults: bool = False, merge_destruct: bool = False
) -> int:
    flags = 0
    if merge_defaults:
        flags |= lib.LYD_MERGE_DEFAULT
    if merge_destruct:
        flags |= lib.LYD_MERGE_DESTRUCT

    return flags


def data_pathtype(path_type_fmt: str):
    if str == "log":
        return lib.LYD_PATH_TYPE

    raise ValueError(f"unknown path type format: {path_type_fmt}")


def anydata_value_type(value, value_type: str):
    if value_type == "datatree":
        val_type = lib.LYD_ANYDATA_DATATREE
    elif value_type == "string":
        val_type = lib.LYD_ANYDATA_STRING
    elif value_type == "xml":
        val_type = lib.LYD_ANYDATA_XML
    elif value_type == "json":
        val_type = lib.LYD_ANYDATA_JSON
    elif value_type == "lyb":
        val_type = lib.LYD_ANYDATA_LYB
    else:
        raise ValueError("unknown anydata valuetype: %r" % value_type)

    if val_type == lib.LYD_ANYDATA_DATATREE:
        if isinstance(value, DNode):
            return value._cdata, val_type
        else:
            raise ValueError(
                f"anydata/anyxml type set to datatree, but value f{value} is of type {type(value)}"
            )

    elif val_type == lib.LYD_ANYDATA_LYB:
        if hasattr(value, "decode"):
            return value, val_type
        else:
            raise ValueError(
                f"anydata/anyxml type set to lyb, bytes expected, but value f{value} is of type {type(value)}"
            )

    elif isinstance(value, str):
        return str2c(value), val_type
    else:
        raise ValueError(
            f"anydata/anyxml type set to xml, json or string, string object expected, but value f{value} is of type {type(value)}"
        )


def data_path_creation_options(opaq=False, output=False, update=False):
    flags = 0
    if opaq:
        flags |= lib.LYD_NEW_PATH_OPAQ
    if output:
        flags |= lib.LYD_NEW_PATH_OUTPUT
    if update:
        flags |= lib.LYD_NEW_PATH_UPDATE


@SchemaFactory.register_subtyped_type_factory("create_node", "struct lyd_node")
@SchemaFactory.register_subtyped_type_factory("create_node", "struct lyd_node_inner")
class DNode(WrapperBase):
    """Representation of data tree node"""

    @property
    def keyword(self) -> str:
        return Node.KEYWORDS.get(self._cdata.nodetype, "unknown")

    factories = {}
    realtypes = {}

    @property
    def schema(self) -> "SCNode":
        return self.context.sf.wrap(self._cdata.schema)

    @property
    def parent(self) -> "DNode":
        return self.context.sf.wrap(self._cdata.parent)

    @property
    def name(self):
        return self.context.sf.wrap(self._cdata.schema.name)

    def __str__(self) -> str:
        return "<%r: %r>" % (type(self).__name__, self.name)

    def module(self):
        return self.context.sf.wrap(lib.lyd_owner_module(self._cdata))

    def metadata(self):
        return self.context.sf.ll2gen(self._cdata.meta)

    def __eq__(self, other: "Dnode") -> bool:
        ret = lib.lyd_compare(self._cdata, other._cdata, 0)
        if ret == lib.LY_SUCCESS:
            return True
        if ret == lib.LY_ENOT:
            return False
        raise self.context.error("libyang node comparasion returned error")

    def __ne__(self, other: "Dnode") -> bool:
        ret = lib.lyd_compare(ffi.cast("struct lyd_node *", self._cdata), ffi.cast("struct lyd_node *", other._cdata), 0)
        if ret == lib.LY_SUCCESS:
            return False
        if ret == lib.LY_ENOT:
            return True
        raise self.context.error("libyang node comparasion returned error")

    def validate(self, no_state: bool = False, present: bool = False) -> "DNode":
        opts = data_validation_options(no_state, present)
        tmp = ffi.new("struct lyd_node **")
        tmp[0] = ffi.cast("struct lyd_node *", self._cdata)
        self.context.check_retval(
            lib.lyd_validate_all(tmp, self.context._cdata, opts, ffi.NULL)
        )
        return self.context.sf.wrap(tmp[0])

    def siblings(self, include_self: bool = True):
        if include_self:
            yield self.context.sf.wrap(self._cdata)

        iterator = self._cdata.prev
        while self._cdata != iterator:
            yield self.context.sf.wrap(iterator)
            iterator = iterator.prev

    def newchild_any(
        self,
        name: str,
        value: Union[str, bytes, "DNode"],
        value_type: str,
        module: "SModule" = None,
    ) -> "DNode":

        val, val_type = anydata_value_type(value, value_type)
        mod = ffi.NULL
        if module:
            mod = module._cdata

        tmp = ffi.new("struct lyd_node **")
        self.context.check_retval(
            # TODO ly_bool output
            lib.lyd_new_any(ffi.cast("struct lyd_node *", self._cdata), mod, str2c(name), val, val_type, tmp)
        )

        return self.context.sf.wrap(tmp[0])

    def newchild_inner(self, name: str, module: "SModule" = None) -> "DNode":
        mod = ffi.NULL
        if module:
            mod = module._cdata
        tmp = ffi.new("struct lyd_node **")
        # TODO ly_bool output
        self.context.check_retval(lib.lyd_new_inner(ffi.cast("struct lyd_node *", self._cdata), mod, str2c(name), 0, tmp))

        return self.context.sf.wrap(tmp[0])

    def newchild_list(
        self, name: str, keys: str = None, module: "SModule" = None
    ) -> "DNode":
        """
        Create new list as a child

        :arg keys: All key values predicate in the form of "[key1='val1'][key2='val2']...",
        they do not have to be ordered. In case of an instance-identifier
        or identityref value, the JSON format is expected
        (module names instead of prefixes).
        Use default value in case of key-less list.
        """

        mod = ffi.NULL
        if module:
            mod = module._cdata
        tmp = ffi.new("struct lyd_node **")
        self.context.check_retval(
            # TODO ly_bool output
            lib.lyd_new_list2(ffi.cast("struct lyd_node *", self._cdata), mod, str2c(name), str2c(keys), 0, tmp)
        )

        return self.context.sf.wrap(tmp[0])

    def newchild_term(self, name: str, value: str, module: "SModule" = None):

        mod = ffi.NULL
        if module:
            mod = module._cdata
        tmp = ffi.new("struct lyd_node **")

        self.context.check_retval(
            # TODO ly_bool output
            lib.lyd_new_term(ffi.cast("struct lyd_node *", self._cdata), mod, str2c(name), str2c(value), 0, tmp)
        )

        return self.context.sf.wrap(tmp[0])

    def newchild_opaq(
        self, name: str, value: str, module: Union[str, "SModule"]
    ) -> "DNode":

        mod = ffi.NULL
        if isinstance(module, str):
            mod = str2c(module)
        elif isinstance(module, "SModule"):
            mod = str2c(module.name)
        else:
            raise TypeError(
                f"module name of type str or reference to module of type SModule expecte, got {module} of type {type(module)}"
            )

        tmp = ffi.new("struct lyd_node **")
        self.context.check_retval(
            lib.lyd_new_opaq(
                ffi.cast("struct lyd_node *", self._cdata), self.context._cdata, str2c(name), str2c(value), mod, tmp)
        )

        return self.context.sf.wrap(tmp[0])

    def find_xpath(self, xpath: str) -> Iterator["Dnode"]:
        dnode_set = ffi.new("struct ly_set **")

        self.context.check_retval(lib.lyd_find_xpath(ffi.cast("struct lyd_node *", self._cdata), dnode_set))
        i = 0
        while i < dnode_set[0].count:
            yield self.context.sf.wrap(dnode_set[i])

    def path(self, pathtype: str = "log") -> str:
        temp = ffi.new("char *")
        ptype = data_pathtype(pathtype)
        self.context.check_retval(lib.lyd_path(ffi.cast("struct lyd_node *", self._cdata), ptype, temp, 0))

        try:
            return c2str(temp)
        finally:
            lib.free(temp)

    def merge(
        self,
        source: "DNode",
        with_siblings: bool = False,
        merge_defaults: bool = False,
        merge_destruct: bool = False,
    ) -> "DNode":
        options = data_merge_options(merge_defaults, merge_destruct)

        if with_siblings:
            self.context.check_retval(
                lib.lyd_merge_siblings(ffi.cast("struct lyd_node *", self._cdata), ffi.cast("struct lyd_node *", source._cdata), options)
            )
        else:
            self.context.check_retval(
                lib.lyd_merge_tree(ffi.cast("struct lyd_node *", self._cdata), source._cdata, options)
            )

    def duplicate(
        self,
        parent: "Dnode" = None,
        with_siblings: bool = False,
        no_meta: bool = False,
        recursive: bool = False,
        with_flags: bool = False,
        with_parents: bool = False,
    ) -> "DNode":
        options = data_duplication_options(no_meta, recursive, with_flags, with_parents)
        par = ffi.NULL
        if parent:
            par = parent._cdata

        temp = ffi.new("struct lyd_node **")

        if with_siblings:
            self.context.check_retval(
                lib.lyd_dup_siblings(ffi.cast("struct lyd_node *", self._cdata), par, options, temp)
            )
        else:
            self.context.check_retval(
                lib.lys_sup_single(ffi.cast("struct lyd_node *", self._cdata), par, options, temp)
            )

        return self.context.sf.wrap(temp[0])

    def insert_child(self, node: "Dnode") -> None:
        """Insert child node"""

        self.context.check_retval(lib.lyd_insert_child(ffi.cast("struct lyd_node *", self._cdata), node._cdata))

    def insert_before(self, node: "Dnode") -> None:
        self.context.lyd_insert_before(lib.lyd_insert_child(ffi.cast("struct lyd_node *", self._cdata), node._cdata))

    def insert_after(self, node: "Dnode") -> None:
        self.context.lyd_insert_after(lib.lyd_insert_child(ffi.cast("struct lyd_node *", self._cdata), node._cdata))

    def insert_sibling(self, node: "Dnode"):
        self.context.lyd_insert_after(
            lib.lyd_insert_child(ffi.cast("struct lyd_node *", self._cdata), node._cdata, ffi.NULL)
        )

    def print(
        self,
        target: TextIO = None,
        fmt: str = "xml",
        print_all: bool = False,
        format: bool = False,
        keep_empty_cont: bool = False,
        wd_all: bool = False,
        wd_all_tag: bool = False,
        wd_explicit: bool = False,
        wd_impl_tag: bool = False,
        wd_mask: bool = False,
        wd_trim: bool = False,
        withsiblings: bool = False,
    ) -> Union[str, None]:
        out_handler = ffi.new("struct ly_out **")
        out_format = data_out_format(fmt)
        flags = data_printer_flags(
            format,
            keep_empty_cont,
            wd_all,
            wd_all_tag,
            wd_explicit,
            wd_impl_tag,
            wd_mask,
            wd_trim,
            withsiblings,
        )

        if target:
            fd = target.fileno()
            self.context.check_retval(lib.ly_out_new_fd(fd, out_handler))
            try:
                if print_all:
                    lib.lyd_print_all(out_handler[0], ffi.cast("struct lyd_node *", self._cdata), out_format, flags)
                else:
                    lib.lyd_print_tree(out_handler[0], ffi.cast("struct lyd_node *", self._cdata), out_format, flags)
            finally:
                lib.ly_out_free(out_handler[0], ffi.NULL, 0)
        else:
            strp = ffi.new("char **")
            self.context.check_retval(lib.ly_out_new_memory(strp, 0, out_handler))
            try:
                if print_all:
                    lib.lyd_print_all(out_handler[0], ffi.cast("struct lyd_node *", self._cdata), out_format, flags)
                else:
                    lib.lyd_print_tree(out_handler[0], ffi.cast("struct lyd_node *", self._cdata), out_format, flags)
                try:
                    return c2str(strp[0])
                finally:
                    lib.free(strp[0])
            finally:
                lib.ly_out_free(out_handler[0], ffi.NULL, 0)

    def unlink(self):
        lib.lyd_unlink_tree(ffi.cast("struct lyd_node *", self._cdata))

    @classmethod
    def add_factory(cls, node_type, realtype):
        def _decor(dnode_factory):
            cls.factories[node_type] = dnode_factory
            cls.realtypes[node_type] = realtype
            return dnode_factory

        return _decor

    @classmethod
    def create_node(cls, cdata, context):
        nodetype = Node.UNKNOWN
        schema = cdata.schema
        if schema:
            nodetype = cdata.schema.nodetype
        casted = ffi.cast(cls.realtypes[nodetype], cdata)
        factory = cls.factories[nodetype]
        return factory(casted, context)


class DNodeInnerBase(DNode):
    def __hash__(self):
        return self._cdata.hash

    def childs(self):
        child = self.context.sf.wrap(self._cdata.child)
        if child:
            yield from child.siblings()
        else:
            yield from ()

    __iter__ = childs


@DNode.add_factory(Node.CONTAINER, "struct lyd_node_inner *")
class DContainer(DNodeInnerBase):
    pass


@DNode.add_factory(Node.LIST, "struct lyd_node_inner *")
class DList(DNodeInnerBase):
    pass


@DNode.add_factory(Node.RPC, "struct lyd_node_inner *")
class DRpc(DNodeInnerBase):
    pass


@DNode.add_factory(Node.ACTION, "struct lyd_node_inner *")
class DAction(DNodeInnerBase):
    pass


@DNode.add_factory(Node.NOTIFICATION, "struct lyd_node_inner *")
class DNotification(DNodeInnerBase):
    pass


# Term nodes
@SchemaFactory.register_type_factory("struct lyd_node_term")
class DNodeTermBase(DNode):
    def __hash__(self):
        return self._cdata.hash

    @property
    def value(self):
        return self.context.sf.wrap(lib.lyd_data_canonic(self._cdata))


@DNode.add_factory(Node.LEAF, "struct lyd_node_term *")
class DLeaf(DNodeTermBase):
    pass


@DNode.add_factory(Node.LEAFLIST, "struct lyd_node_term *")
class DLeafList(DNodeTermBase):
    pass


# anydata/anyxml nodes
@SchemaFactory.register_type_factory("struct lyd_node_any")
class DNodeAnyBase(DNode):
    def __hash__(self):
        return self._cdata.hash

    @property
    def value(self) -> Union["Dnode", str, bytes]:
        if self._cdata.valu_type == lib.LYD_ANYDATA_DATATREE:
            return self.context.sf.wrap(self._cdata.value.tree)

        if self._cdata.valu_type == lib.LYD_ANYDATA_STRING:
            return self.context.sf.wrap(self._cdata.value.str)

        if self._cdata.valu_type == lib.LYD_ANYDATA_XML:
            return self.context.sf.wrap(self._cdata.value.xml)

        if self._cdata.valu_type == lib.LYD_ANYDATA_JSON:
            return self.context.sf.wrap(self._cdata.value.json)

        if self._cdata.valu_type == lib.LYD_ANYDATA_LYB:
            return self._cdata.value.str


@DNode.add_factory(Node.ANYDATA, "struct lyd_node_any *")
class DNodeAnydata(DNodeAnyBase):
    pass


@DNode.add_factory(Node.ANYXML, "struct lyd_node_any *")
class DNodeAnyxml(DNodeAnyBase):
    pass


# opaque node
@SchemaFactory.register_type_factory("struct lyd_node_opaq")
@DNode.add_factory(Node.UNKNOWN, "struct lyd_node_opaq *")
class DNodeOpaque(DNode):
    @property
    def name(self):
        # todo
        pass
        # return self.context.sf.wrap(self._cdata.name)

    @property
    def prefix(self):
        # todo
        pass
        # return self.context.sf.wrap(self._cdata.prefix.pref)

    @property
    def namespace(self):
        # todo
        pass
        # return self.context.sf.wrap(self._cdata.prefix.ns)

    @property
    def value(self):
        pass
        # todo
        # return self.context.sf.wrap(self._cdata.value)


@SchemaFactory.register_type_factory("struct lyd_meta")
class DMetadata(WrapperBase):
    @property
    def owner(self):
        return self.context.sf.wrap()

    @property
    def annotation(self) -> "SCExtension":
        return self.context.sf.wrap(self._cdata.annotation)

    @property
    def name(self) -> str:
        return self.context.sf.wrap(self._cdata.name)

    @property
    def value(self) -> str:
        return self.context.sf.wrap(self._cdata.value.original)

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        pass
