# Copyright (c) 2020 6WIND S.A.
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

import logging
from typing import IO, Any, Dict, Iterator, Optional, Union

from _libyang import ffi, lib
from .keyed_list import KeyedList
from .schema import (
    Module,
    SContainer,
    SLeaf,
    SLeafList,
    SList,
    SNode,
    SNotif,
    SRpc,
    Type,
)
from .util import LibyangError, c2str, str2c, IO_type, DataType


LOG = logging.getLogger(__name__)


# -------------------------------------------------------------------------------------
def printer_flags(
    keepemptycont: bool = False,
    shrink: bool = False,
    wd_all: bool = False,
    wd_all_tag: bool = False,
    wd_explicit: bool = False,
    wd_impl_tag: bool = False,
    wd_trim: bool = False,
    with_siblings: bool = False,
) -> int:
    flags = 0
    if wd_impl_tag:
        flags |= lib.LYD_PRINT_KEEPEMPTYCONT
    if shrink:
        flags |= lib.LYD_PRINT_SHRINK
    if wd_all:
        flags |= lib.LYD_PRINT_WD_ALL
    if wd_all_tag:
        flags |= lib.LYD_PRINT_WD_ALL_TAG
    if wd_explicit:
        flags |= lib.LYD_PRINT_WD_EXPLICIT
    if wd_impl_tag:
        flags |= lib.LYD_PRINT_WD_IMPL_TAG
    if wd_trim:
        flags |= lib.LYD_PRINT_WD_TRIM
    if with_siblings:
        flags |= lib.LYD_PRINT_WITHSIBLINGS
    return flags


# -------------------------------------------------------------------------------------
def data_format(fmt_string: str) -> int:
    if fmt_string == "json":
        return lib.LYD_JSON
    if fmt_string == "xml":
        return lib.LYD_XML
    if fmt_string == "lyb":
        return lib.LYD_LYB
    raise ValueError("unknown data format: %r" % fmt_string)


# -------------------------------------------------------------------------------------
def path_flags(
    update: bool = False, rpc_output: bool = False, no_parent_ret: bool = False
) -> int:
    flags = 0
    if update:
        flags |= lib.LYD_NEW_PATH_UPDATE
    if rpc_output:
        flags |= lib.LYD_NEW_PATH_OUTPUT
    return flags


# -------------------------------------------------------------------------------------
def parser_flags(
    lyb_mod_update: bool = False,
    no_state: bool = False,
    parse_only: bool = False,
    opaq: bool = False,
    ordered: bool = False,
    strict: bool = False
) -> int:
    flags = 0
    if lyb_mod_update:
        flags |= lib.LYD_PARSE_LYB_MOD_UPDATE
    if no_state:
        flags |= lib.LYD_PARSE_NO_STATE
    if parse_only:
        flags |= lib.LYD_PARSE_ONLY
    if opaq:
        flags |= lib.LYD_PARSE_OPAQ
    if ordered:
        flags |= lib.LYD_PARSE_ORDERED
    if strict:
        flags |= lib.LYD_PARSE_STRICT
    return flags


# -------------------------------------------------------------------------------------
def merge_flags(
    defaults: bool = False,
    destruct: bool = False,
    with_flags: bool = False,
) -> int:
    flags = 0
    if defaults:
        flags |= lib.LYD_MERGE_DEFAULTS
    if destruct:
        flags |= lib.LYD_MERGE_DESTRUCT
    if with_flags:
        flags |= lib.LYD_MERGE_WITH_FLAGS
    return flags


# -------------------------------------------------------------------------------------
def data_type(dtype):
    if dtype == DataType.DATA_YANG:
        return lib.LYD_TYPE_DATA_YANG
    elif dtype == DataType.RPC_YANG:
        return lib.LYD_TYPE_RPC_YANG
    elif dtype == DataType.NOTIF_YANG:
        return lib.LYD_TYPE_NOTIF_YANG
    elif dtype == DataType.REPLY_YANG:
        return lib.LYD_TYPE_REPLY_YANG
    elif dtype == DataType.RPC_NETCONF:
        return lib.LYD_TYPE_RPC_NETCONF
    elif dtype == DataType.NOTIF_NETCONF:
        return lib.LYD_TYPE_NOTIF_NETCONF
    elif dtype == DataType.REPLY_NETCONF:
        return lib.LYD_TYPE_REPLY_NETCONF
    raise ValueError('Unknown data type')


# -------------------------------------------------------------------------------------
def validation_flags(
    no_state: bool = False,
    validate_present: bool = False
) -> int:
    flags = 0
    if no_state:
        flags |= lib.LYD_VALIDATE_NO_STATE
    if validate_present:
        flags |= lib.LYD_VALIDATE_PRESENT
    return flags


def diff_flags(
    with_defaults: bool = False
) -> int:
    flags = 0
    if with_defaults:
        flags |= lib.LYD_DIFF_DEFAULTS
    return flags


# -------------------------------------------------------------------------------------
class DDiff:
    """
    Data tree diff
    """

    __slots__ = ("dtype", "first", "second")

    def __init__(self, dtype, first: Optional["DNode"], second: Optional["DNode"]):
        """
        :arg dtype:
            The type of the diff
        :arg first:
            The first DNode
        :arg second:
            The second DNode
        """
        self.dtype = dtype
        self.first = first
        self.second = second

    def diff_type(self) -> str:
        """Get diff type as string"""
        return self.DIFF_TYPES.get(self.dtype, "unknown")

    def __repr__(self) -> str:
        return "<libyang.data.DDiff {} first={} second={}>".format(
            self.diff_type(), self.first, self.second
        )


# -------------------------------------------------------------------------------------
class DNode:
    """
    Data tree node.
    """

    __slots__ = ("context", "cdata")

    def __init__(self, context: "libyang.Context", cdata):
        """
        :arg context:
            The libyang.Context python object.
        :arg cdata:
            The pointer to the C structure allocated by libyang.so.
        """
        self.context = context
        self.cdata = cdata  # C type: "struct lyd_node *"

    def meta(self):
        ret = {}
        item = self.cdata.meta
        while item != ffi.NULL:
            ret[c2str(item.name)] = c2str(lib.lyd_value_get_canonical(self.context.cdata, ffi.addressof(item.value)))
            item = item.next
        return ret

    def new_path(self, path: str,
                 value: str,
                 opt_update: bool = False,
                 opt_output: bool = False,
                 opt_opaq: bool = False,
                 opt_bin_value: bool = False,
                 opt_canon_value: bool = False):

        opt = 0
        if opt_update:
            opt |= lib.LYD_NEWOPT_UPDATE
        if opt_output:
            opt |= lib.LYD_NEW_PATH_OUTPUT
        if opt_opaq:
            opt |= lib.LYD_NEW_PATH_OPAQ
        if opt_bin_value:
            opt |= lib.LYD_NEW_PATH_BIN_VALUE
        if opt_canon_value:
            opt |= lib.LYD_NEW_PATH_CANON_VALUE

        ret = lib.lyd_new_path(self.cdata, ffi.NULL, str2c(path), str2c(value), opt, ffi.NULL)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot get module")

    def insert_child(self, node):
        ret = lib.lyd_insert_child(self.cdata, node.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot insert node")

    def name(self) -> str:
        return c2str(self.cdata.schema.name)

    def module(self) -> Module:
        if not self.cdata.schema:
            raise self.context.error("cannot get module")
        return Module(self.context, self.cdata.schema.module)

    def schema(self) -> SNode:
        return SNode.new(self.context, self.cdata.schema)

    def parent(self) -> Optional["DNode"]:
        if not self.cdata.parent:
            return None
        return self.new(self.context, self.cdata.parent)

    def next(self) -> Optional["DNode"]:
        if not self.cdata.next:
            return None
        return self.new(self.context, self.cdata.next)

    def prev(self) -> Optional["DNode"]:
        if not self.cdata.prev:
            return None
        return self.new(self.context, self.cdata.prev)

    def root(self) -> "DNode":
        node = self
        while node.parent() is not None:
            node = node.parent()
        return node

    def first_sibling(self) -> "DNode":
        n = lib.lyd_first_sibling(self.cdata)
        if n == self.cdata:
            return self
        return self.new(self.context, n)

    def siblings(self, include_self: bool = True) -> Iterator["DNode"]:
        n = lib.lyd_first_sibling(self.cdata)
        while n:
            if n == self.cdata:
                if include_self:
                    yield self
            else:
                yield self.new(self.context, n)
            n = n.next

    def find_path(self, path: str, output: bool = False):
        node = ffi.new("struct lyd_node **")
        ret = lib.lyd_find_path(self.cdata, str2c(path), output, node)
        if ret == lib.LY_SUCCESS or ret == lib.LY_EINCOMPLETE:
            return DNode.new(self.context, node[0])
        return None

    def find_one(self, xpath: str) -> Optional["DNode"]:
        try:
            return next(self.find_all(xpath))
        except StopIteration:
            return None

    def find_all(self, xpath: str) -> Iterator["DNode"]:
        node_set = ffi.new("struct ly_set **")
        ret = lib.lyd_find_xpath(self.cdata, str2c(xpath), node_set)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot find path: %s", xpath)

        node_set = node_set[0]
        try:
            for i in range(node_set.count):
                n = DNode.new(self.context, node_set.dnodes[i])
                yield n
        finally:
            lib.ly_set_free(node_set, ffi.NULL)

    def path(self) -> str:
        path = lib.lyd_path(self.cdata, lib.LYD_PATH_STD, ffi.NULL, 0)
        try:
            return c2str(path)
        finally:
            lib.free(path)

    def validate(
        self,
        no_state: bool = False,
        validate_present: bool = False,
    ) -> None:
        if self.cdata.parent:
            raise self.context.error("validation is only supported on top-level nodes")
        flags = validation_flags(
            no_state=no_state,
            validate_present=validate_present,
        )
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata
        ret = lib.lyd_validate_all(node_p, self.context.cdata, flags, ffi.NULL)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("validation failed")

    def validate_op(
        self,
        dtype: DataType,
    ) -> None:
        dtype = data_type(dtype)
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata
        ret = lib.lyd_validate_op(node_p[0], ffi.NULL, dtype, ffi.NULL)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("validation failed")

    def diff(
        self,
        other: "DNode",
        no_siblings: bool = False,
        with_defaults: bool = False,
    ) -> Iterator[DDiff]:
        flags = diff_flags(with_defaults=with_defaults)
        node_p = ffi.new("struct lyd_node **")
        if no_siblings:
            ret = lib.lyd_diff_tree(self.cdata, other.cdata, flags, node_p)
        else:
            ret = lib.lyd_diff_siblings(self.cdata, other.cdata, flags, node_p)

        if ret != lib.LY_SUCCESS:
            raise self.context.error("diff error")

        return self.new(self.context, node_p[0])

    def diff_apply(
        self,
        diff_node: "DNode"
    ) -> None:
        #node = ffi.addressof()
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata

        #node_p = ffi.addressof(self.cdata)
        ret = lib.lyd_diff_apply_all(node_p, diff_node.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("apply diff error")

    def merge(
        self,
        source: "DNode",
        with_siblings: bool = False,
        defaults: bool = False,
        destruct: bool = False,
        with_flags: bool = False,
    ) -> None:
        flags = merge_flags(
            defaults=defaults, destruct=destruct, with_flags=with_flags
        )
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata
        if with_siblings:
            ret = lib.lyd_merge_siblings(node_p, source.cdata, flags)
        else:
            ret = lib.lyd_merge_tree(node_p, source.cdata, flags)

        if ret != lib.LY_SUCCESS:
            raise self.context.error("merge failed")

    def print(
        self,
        fmt: str,
        out_type: IO_type,
        out_target: Union[IO, str, None] = None,
        printer_keepemptycont: bool = False,
        printer_shrink: bool = False,
        printer_wd_all: bool = False,
        printer_wd_all_tag: bool = False,
        printer_wd_explicit: bool = False,
        printer_wd_impl_tag: bool = False,
        printer_wd_trim: bool = False,
        printer_with_siblings: bool = False,
    ) -> Union[str, bytes]:
        flags = printer_flags(
            keepemptycont=printer_keepemptycont,
            shrink=printer_shrink,
            wd_all=printer_wd_all,
            wd_all_tag=printer_wd_all_tag,
            wd_explicit=printer_wd_explicit,
            wd_impl_tag=printer_wd_impl_tag,
            wd_trim=printer_wd_trim,
        )
        fmt = data_format(fmt)
        out_data = ffi.new("struct ly_out **")

        if out_type == IO_type.FD:
            raise NotImplementedError

        elif out_type == IO_type.FILE:
            raise NotImplementedError

        elif out_type == IO_type.FILEPATH:
            raise NotImplementedError

        elif out_type == IO_type.MEMORY:

            buf = ffi.new("char **")
            ret = lib.ly_out_new_memory(buf, 0, out_data)
            if ret != lib.LY_SUCCESS:
                raise self.context.error("failed to initialize output target")

            if printer_with_siblings:
                ret = lib.lyd_print_all(out_data[0], self.cdata, fmt, flags)
            else:
                ret = lib.lyd_print_tree(out_data[0], self.cdata, fmt, flags)

            lib.ly_out_free(out_data[0], ffi.NULL, 0)
            if ret != lib.LY_SUCCESS:
                raise self.context.error("failed to write data")

            ret = c2str(buf[0], decode=True)

        else:
            raise ValueError('no input specified')

        return ret

    def print_mem(
        self,
        fmt: str,
        printer_keepemptycont: bool = False,
        printer_shrink: bool = False,
        printer_wd_all: bool = False,
        printer_wd_all_tag: bool = False,
        printer_wd_explicit: bool = False,
        printer_wd_impl_tag: bool = False,
        printer_wd_trim: bool = False,
        printer_with_siblings: bool = False,
    ) -> Union[str, bytes]:
        flags = printer_flags(
            keepemptycont=printer_keepemptycont,
            shrink=printer_shrink,
            wd_all=printer_wd_all,
            wd_all_tag=printer_wd_all_tag,
            wd_explicit=printer_wd_explicit,
            wd_impl_tag=printer_wd_impl_tag,
            wd_trim=printer_wd_trim,
            with_siblings=printer_with_siblings
        )
        buf = ffi.new("char **")
        fmt = data_format(fmt)
        ret = lib.lyd_print_mem(buf, self.cdata, fmt, flags)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot print node")
        try:
            if fmt == lib.LYD_LYB:
                # binary format, do not convert to unicode
                return c2str(buf[0], decode=False)
            return c2str(buf[0], decode=True)
        finally:
            lib.free(buf[0])

    def print_file(
        self,
        fileobj: IO,
        fmt: str,
        with_siblings: bool = False,
        include_implicit_defaults: bool = False,
        trim_default_values: bool = False,
        keep_empty_containers: bool = False,
    ) -> None:
        flags = printer_flags(
            with_siblings=with_siblings,
            include_implicit_defaults=include_implicit_defaults,
            trim_default_values=trim_default_values,
            keep_empty_containers=keep_empty_containers,
        )
        fmt = data_format(fmt)
        ret = lib.lyd_print_fd(fileobj.fileno(), self.cdata, fmt, flags)
        if ret != 0:
            raise self.context.error("cannot print node")

    def print_dict(
        self,
        strip_prefixes: bool = True,
        absolute: bool = True,
        with_siblings: bool = False,
    ) -> Dict[str, Any]:
        """
        Convert a DNode object to a python dictionary.

        :arg bool strip_prefixes:
            If True (the default), module prefixes are stripped from dictionary keys. If
            False, dictionary keys are in the form ``<module>:<name>``.
        :arg bool absolute:
            If True (the default), always return a dictionary containing the complete
            tree starting from the root.
        :arg bool with_siblings:
            If True, include the node's siblings.
        """
        name_cache = {}

        def _node_name(node):
            name = name_cache.get(node.schema)
            if name is None:
                if strip_prefixes:
                    name = c2str(node.schema.name)
                else:
                    mod = node.schema.module
                    name = "%s:%s" % (c2str(mod.name), c2str(node.schema.name))
                name_cache[node.schema] = name
            return name

        list_keys_cache = {}

        def _init_yang_list(snode):
            if snode.flags & lib.LYS_ORDBY_USER:
                return []  # ordered list, return an empty builtin list

            # unordered lists
            if snode.nodetype == SNode.LEAFLIST:
                return KeyedList(key_name=None)

            if snode not in list_keys_cache:
                keys = []
                child = lib.lysc_node_child(snode)
                while child:
                    if child.flags & lib.LYS_KEY:
                        if strip_prefixes:
                            keys.append(c2str(child.name))
                        else:
                            keys.append("%s:%s" % (c2str(child.module.name), c2str(child.name)))
                    child = child.next
                if len(keys) == 1:
                    list_keys_cache[snode] = keys[0]
                else:
                    list_keys_cache[snode] = tuple(keys)

            return KeyedList(key_name=list_keys_cache[snode])

        def _to_dict(node, parent_dic):
            name = _node_name(node)
            if node.schema.nodetype == SNode.LIST:
                list_element = {}

                child = lib.lyd_child(node)
                while child:
                    _to_dict(child, list_element)
                    child = child.next
                if name not in parent_dic:
                    parent_dic[name] = _init_yang_list(node.schema)
                parent_dic[name].append(list_element)
            elif node.schema.nodetype & (
                SNode.CONTAINER | SNode.RPC | SNode.ACTION | SNode.NOTIF
            ):
                container = {}
                child = lib.lyd_child(node)
                while child:
                    _to_dict(child, container)
                    child = child.next
                parent_dic[name] = container
            elif node.schema.nodetype == SNode.LEAFLIST:
                if name not in parent_dic:
                    parent_dic[name] = _init_yang_list(node.schema)
                parent_dic[name].append(DLeaf.cdata_leaf_value(node))
            elif node.schema.nodetype == SNode.LEAF:
                parent_dic[name] = DLeaf.cdata_leaf_value(node)

        dic = {}
        dnode = self
        if absolute:
            dnode = dnode.root()
        if with_siblings:
            for sib in dnode.siblings():
                _to_dict(sib.cdata, dic)
        else:
            _to_dict(dnode.cdata, dic)
        return dic

    def merge_data_dict(
        self,
        dic: Dict[str, Any],
        no_state: bool = False,
        validate_present: bool = False,
        validate: bool = True,
        strict: bool = False,
        operation_type: DataType = None,
    ) -> Optional["DNode"]:
        """
        Merge a python dictionary into this node. The returned value is the first
        created node.

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
        :arg operation_type:
            The operation cannot be determined automatically since RPC/action and a reply to it share
            the common top level node referencing the RPC/action schema node and may not have any
            input/output children to use for distinction. See DataType for options.
        """
        return dict_to_dnode(
            dic,
            self.module(),
            parent=self,
            no_state=no_state,
            validate_present=validate_present,
            validate=validate,
            strict=strict,
            operation_type=operation_type,
        )

    def free(self, with_siblings: bool = True) -> None:
        try:
            if with_siblings:
                lib.lyd_free_all(self.cdata)
            else:
                lib.lyd_free_tree(self.cdata)
        finally:
            self.cdata = None

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()

    NODETYPE_CLASS = {}

    @classmethod
    def register(cls, *nodetypes):
        def _decorator(nodeclass):
            for t in nodetypes:
                cls.NODETYPE_CLASS[t] = nodeclass
            return nodeclass

        return _decorator

    @classmethod
    def new(cls, context: "libyang.Context", cdata) -> "DNode":
        cdata = ffi.cast("struct lyd_node *", cdata)
        nodecls = cls.NODETYPE_CLASS.get(cdata.schema.nodetype, None)
        if nodecls is None:
            raise TypeError("node type %s not implemented" % cdata.schema.nodetype)
        return nodecls(context, cdata)


# -------------------------------------------------------------------------------------
@DNode.register(SNode.CONTAINER)
class DContainer(DNode):
    def create_path(
        self, path: str, value: Any = None, rpc_output: bool = False
    ) -> Optional[DNode]:
        return self.context.create_data_path(
            path, parent=self, value=value, rpc_output=rpc_output
        )

    def children(self) -> Iterator[DNode]:
        child = lib.lyd_child_no_keys(self.cdata)
        while child:
            if child.schema != ffi.NULL:
                yield DNode.new(self.context, child)
            child = child.next

    def __iter__(self):
        return self.children()


# -------------------------------------------------------------------------------------
@DNode.register(SNode.RPC)
@DNode.register(SNode.ACTION)
class DRpc(DContainer):
    pass


# -------------------------------------------------------------------------------------
@DNode.register(SNode.LIST)
class DList(DContainer):
    pass


# -------------------------------------------------------------------------------------
@DNode.register(SNode.LEAF)
class DLeaf(DNode):
    def value(self) -> Any:
        return DLeaf.cdata_leaf_value(self.cdata)

    @staticmethod
    def cdata_leaf_value(cdata) -> Any:

        val = lib.lyd_get_value(cdata)
        if val == ffi.NULL:
            return None

        val = c2str(val)
        term_node = ffi.cast("struct lyd_node_term *", cdata)
        val_type = ffi.new("const struct lysc_type **", ffi.NULL)

        # get real value type
        ret = lib.lyd_value_validate(ffi.NULL, term_node.schema, str2c(val),
                                     len(val), ffi.NULL, val_type, ffi.NULL)

        if ret == lib.LY_SUCCESS or ret == lib.LY_EINCOMPLETE:
            val_type = val_type[0].basetype
            if val_type == Type.BOOL:
                return True if val == 'true' else False
            elif val_type in Type.NUM_TYPES:
                return int(val)
            return val

        raise TypeError('value type validation error')


# -------------------------------------------------------------------------------------
@DNode.register(SNode.LEAFLIST)
class DLeafList(DLeaf):
    pass


# -------------------------------------------------------------------------------------
@DNode.register(SNode.NOTIF)
class DNotif(DContainer):
    pass


# -------------------------------------------------------------------------------------
@DNode.register(SNode.ANYXML)
class DAnyxml(DNode):
    def value(self, fmt: str = 'xml'):
        anystr = ffi.new('char **', ffi.NULL)
        ret = lib.lyd_any_value_str(self.cdata, anystr)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot get data")
        return c2str(anystr[0])


# -------------------------------------------------------------------------------------
@DNode.register(SNode.ANYDATA)
class DAnydata(DNode):
    def value(self, fmt: str = 'xml'):
        anystr = ffi.new('char **', ffi.NULL)
        ret = lib.lyd_any_value_str(self.cdata, anystr)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot get data")
        return c2str(anystr[0])


# -------------------------------------------------------------------------------------
def dict_to_dnode(
    dic: Dict[str, Any],
    module: Module,
    parent: Optional[DNode] = None,
    no_state: bool = False,
    validate_present: bool = False,
    validate: bool = True,
    strict: bool = False,
    operation_type: DataType = None,
) -> Optional[DNode]:
    """
    Convert a python dictionary to a DNode object given a YANG module object. The return
    value is the first created node. If parent is not set, a top-level node is returned.

    :arg dic:
        The python dictionary to convert.
    :arg module:
        The libyang Module object associated with the dictionary.
    :arg parent:
        Optional parent to update. If not specified a new top-level DNode will be
        created.
    :arg no_state:
        Consider state data not allowed and raise an error during validation if they are found.
    :arg validate_present:
        Validate result of the operation against schema.
    :arg validate:
        Run validation on result of the operation.
    :arg strict:
        Instead of ignoring data without schema definition, raise an error.
    :arg operation_type:
        The operation cannot be determined automatically since RPC/action and a reply to it share
        the common top level node referencing the RPC/action schema node and may not have any
        input/output children to use for distinction. See DataType for options.
    """
    if not dic:
        return None

    if not isinstance(dic, dict):
        raise TypeError("dic argument must be a python dict")
    if not isinstance(module, Module):
        raise TypeError("module argument must be a Module object")
    if parent is not None and not isinstance(parent, DNode):
        raise TypeError("parent argument must be a DNode object or None")

    rpcreply = False
    if operation_type == DataType.REPLY_YANG or operation_type == DataType.REPLY_NETCONF:
        rpcreply = True

    created = []

    def _create_leaf(_parent, module, name, value, in_rpc_output=False):
        if value is not None:
            if isinstance(value, bool):
                value = str(value).lower()
            elif not isinstance(value, str):
                value = str(value)

        n = ffi.new('struct lyd_node **')
        ret = lib.lyd_new_term(_parent, module.cdata, str2c(name), str2c(value), in_rpc_output, n)

        if ret != lib.LY_SUCCESS:
            if _parent:
                parent_path = repr(DNode.new(module.context, _parent).path())
            else:
                parent_path = "module %r" % module.name()
            raise module.context.error(
                "failed to create leaf %r as a child of %s", name, parent_path
            )
        created.append(n[0])

    def _create_container(_parent, module, name, in_rpc_output=False):
        n = ffi.new('struct lyd_node **')
        ret = lib.lyd_new_inner(_parent, module.cdata, str2c(name), in_rpc_output, n)
        if ret != lib.LY_SUCCESS:
            if _parent:
                parent_path = repr(DNode.new(module.context, _parent).path())
            else:
                parent_path = "module %r" % module.name()
            raise module.context.error(
                "failed to create container/list/rpc %r as a child of %s",
                name,
                parent_path,
            )
        created.append(n[0])
        return n[0]

    def _create_list(_parent, module, name, key_values, in_rpc_output=False):
        n = ffi.new('struct lyd_node **')
        ret = lib.lyd_new_list(_parent, module.cdata, str2c(name), in_rpc_output, n, *[str2c(i) for i in key_values])
        if ret != lib.LY_SUCCESS:
            if _parent:
                parent_path = repr(DNode.new(module.context, _parent).path())
            else:
                parent_path = "module %r" % module.name()
            raise module.context.error(
                "failed to create container/list/rpc %r as a child of %s",
                name,
                parent_path,
            )
        created.append(n[0])
        return n[0]

    schema_cache = {}

    def _find_schema(schema_parent, name, prefix):
        cache_key = (schema_parent.cdata, name, prefix)
        snode, module = schema_cache.get(cache_key, (None, None))
        if snode is not None:
            return snode, module
        if isinstance(schema_parent, SRpc):
            if rpcreply:
                schema_parent = schema_parent.output()
            else:
                schema_parent = schema_parent.input()

            if schema_parent is None:
                # there may not be any input or any output node in the rpc
                return None, None
        for s in schema_parent:
            if s.name() != name:
                continue
            mod = s.module()
            if prefix is not None and mod.name() != prefix:
                continue
            snode = s
            module = mod
            break
        schema_cache[cache_key] = (snode, module)
        return snode, module

    keys_cache = {}

    def _dic_keys(_dic, _schema):
        if isinstance(_schema, SList):
            # list keys must be first and in the order specified in the schema
            list_keys = keys_cache.get(_schema.cdata, None)
            if list_keys is None:
                list_keys = tuple(k.name() for k in _schema.keys())
                keys_cache[_schema.cdata] = list_keys
            keys = []
            for k in list_keys:
                if k in _dic:
                    keys.append(k)
            keys.extend(_dic.keys() - list_keys)
            return keys
        return _dic.keys()

    def _to_dnode(_dic, _schema, _parent=ffi.NULL, in_rpc_output=False):
        for key in _dic_keys(_dic, _schema):
            if ":" in key:
                prefix, name = key.split(":")
            else:
                prefix, name = None, key

            s, module = _find_schema(_schema, name, prefix)
            if not s:
                if isinstance(_schema, Module):
                    path = _schema.name()
                elif isinstance(_schema, SNode):
                    path = _schema.schema_path()
                else:
                    path = str(_schema)
                if strict:
                    raise LibyangError("%s: unknown element %r" % (path, key))
                LOG.warning("%s: skipping unknown element %r", path, key)
                continue

            value = _dic[key]

            if isinstance(s, SLeaf):
                _create_leaf(_parent, module, name, value, in_rpc_output)

            elif isinstance(s, SLeafList):
                if not isinstance(value, (list, tuple)):
                    raise TypeError(
                        "%s: python value is not a list/tuple: %r"
                        % (s.schema_path(), value)
                    )
                for v in value:
                    _create_leaf(_parent, module, name, v, in_rpc_output)

            elif isinstance(s, SRpc):
                n = _create_container(_parent, module, name, in_rpc_output)
                _to_dnode(value, s, n, rpcreply)

            elif isinstance(s, SContainer):
                n = _create_container(_parent, module, name, in_rpc_output)
                _to_dnode(value, s, n, in_rpc_output)

            elif isinstance(s, SList):
                if not isinstance(value, (list, tuple)):
                    raise TypeError(
                        "%s: python value is not a list/tuple: %r"
                        % (s.schema_path(), value)
                    )

                keys = [i.name() for i in s.keys()]
                for v in value:
                    if not isinstance(v, dict):
                        raise TypeError(
                            "%s: list element is not a dict: %r"
                            % (_schema.schema_path(), v)
                        )
                    val = v.copy()
                    key_values = []
                    for k in keys:
                        try:
                            key_values.append(val.pop(k))
                        except KeyError:
                            raise ValueError('Missing key %s in the list' % (k))

                    n = _create_list(_parent, module, name, key_values, in_rpc_output)
                    _to_dnode(val, s, n, in_rpc_output)

            elif isinstance(s, SNotif):
                n = _create_container(_parent, module, name, in_rpc_output)
                _to_dnode(value, s, n, in_rpc_output)

    result = None

    try:
        if parent is not None:
            _parent = parent.cdata
            _schema_parent = parent.schema()
        else:
            _parent = ffi.NULL
            _schema_parent = module

        _to_dnode(
            dic,
            _schema_parent,
            _parent,
            in_rpc_output=rpcreply and isinstance(parent, DRpc),
        )
        if created:
            result = DNode.new(module.context, created[0])
            if validate:
                if operation_type is None:
                    result.root().validate(no_state=no_state, validate_present=validate_present)
                else:
                    result.root().validate_op(operation_type)

    except:
        for c in reversed(created):
            lib.lyd_free_tree(c)
        raise

    return result
