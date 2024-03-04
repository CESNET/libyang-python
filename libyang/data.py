# Copyright (c) 2020 6WIND S.A.
# Copyright (c) 2021 RACOM s.r.o.
# SPDX-License-Identifier: MIT

import logging
from typing import IO, Any, Dict, Iterator, Optional, Tuple, Union

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
from .util import DataType, IOType, LibyangError, c2str, ly_array_iter, str2c


LOG = logging.getLogger(__name__)


# -------------------------------------------------------------------------------------
def implicit_flags(
    no_config: bool = False,
    no_defaults: bool = False,
    no_state: bool = False,
    output: bool = False,
) -> int:
    flags = 0
    if no_config:
        flags |= lib.LYD_IMPLICIT_NO_CONFIG
    if no_state:
        flags |= lib.LYD_IMPLICIT_NO_STATE
    if no_defaults:
        flags |= lib.LYD_IMPLICIT_NO_DEFAULTS
    if output:
        flags |= lib.LYD_IMPLICIT_OUTPUT
    return flags


# -------------------------------------------------------------------------------------
def printer_flags(
    with_siblings: bool = False,
    pretty: bool = True,
    keep_empty_containers: bool = False,
    trim_default_values: bool = False,
    include_implicit_defaults: bool = False,
) -> int:
    flags = 0
    if with_siblings:
        flags |= lib.LYD_PRINT_WITHSIBLINGS
    if not pretty:
        flags |= lib.LYD_PRINT_SHRINK
    if keep_empty_containers:
        flags |= lib.LYD_PRINT_KEEPEMPTYCONT
    if trim_default_values:
        flags |= lib.LYD_PRINT_WD_TRIM
    if include_implicit_defaults:
        flags |= lib.LYD_PRINT_WD_ALL
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
def newval_flags(
    rpc_output: bool = False,
    store_only: bool = False,
    bin_value: bool = False,
    canon_value: bool = False,
    meta_clear_default: bool = False,
    update: bool = False,
    opaq: bool = False,
) -> int:
    """
    Translate from booleans to newvaloptions flags.
    """
    flags = 0
    if rpc_output:
        flags |= lib.LYD_NEW_VAL_OUTPUT
    if store_only:
        flags |= lib.LYD_NEW_VAL_STORE_ONLY
    if bin_value:
        flags |= lib.LYD_NEW_VAL_BIN
    if canon_value:
        flags |= lib.LYD_NEW_VAL_CANON
    if meta_clear_default:
        flags |= lib.LYD_NEW_META_CLEAR_DFLT
    if update:
        flags |= lib.LYD_NEW_PATH_UPDATE
    if opaq:
        flags |= lib.LYD_NEW_PATH_OPAQ
    return flags


# -------------------------------------------------------------------------------------
def parser_flags(
    lyb_mod_update: bool = False,
    no_state: bool = False,
    parse_only: bool = False,
    opaq: bool = False,
    ordered: bool = False,
    strict: bool = False,
    store_only: bool = False,
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
    if store_only:
        flags |= lib.LYD_PARSE_STORE_ONLY
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
def dup_flags(
    no_meta: bool = False,
    recursive: bool = False,
    with_flags: bool = False,
    with_parents: bool = False,
) -> int:
    flags = 0
    if no_meta:
        flags |= lib.LYD_DUP_NO_META
    if recursive:
        flags |= lib.LYD_DUP_RECURSIVE
    if with_flags:
        flags |= lib.LYD_DUP_WITH_FLAGS
    if with_parents:
        flags |= lib.LYD_DUP_WITH_PARENTS
    return flags


# -------------------------------------------------------------------------------------
def data_type(dtype):
    if dtype == DataType.DATA_YANG:
        return lib.LYD_TYPE_DATA_YANG
    if dtype == DataType.RPC_YANG:
        return lib.LYD_TYPE_RPC_YANG
    if dtype == DataType.NOTIF_YANG:
        return lib.LYD_TYPE_NOTIF_YANG
    if dtype == DataType.REPLY_YANG:
        return lib.LYD_TYPE_REPLY_YANG
    if dtype == DataType.RPC_NETCONF:
        return lib.LYD_TYPE_RPC_NETCONF
    if dtype == DataType.NOTIF_NETCONF:
        return lib.LYD_TYPE_NOTIF_NETCONF
    if dtype == DataType.REPLY_NETCONF:
        return lib.LYD_TYPE_REPLY_NETCONF
    raise ValueError("Unknown data type")


# -------------------------------------------------------------------------------------
def validation_flags(
    no_state: bool = False,
    validate_present: bool = False,
    validate_multi_error: bool = False,
) -> int:
    flags = 0
    if no_state:
        flags |= lib.LYD_VALIDATE_NO_STATE
    if validate_present:
        flags |= lib.LYD_VALIDATE_PRESENT
    if validate_multi_error:
        flags |= lib.LYD_VALIDATE_MULTI_ERROR
    return flags


def diff_flags(with_defaults: bool = False) -> int:
    flags = 0
    if with_defaults:
        flags |= lib.LYD_DIFF_DEFAULTS
    return flags


# -------------------------------------------------------------------------------------
class DNodeAttrs:
    __slots__ = ("context", "parent", "cdata", "__dict__")

    def __init__(self, context: "libyang.Context", parent: "libyang.DNode"):
        self.context = context
        self.parent = parent
        self.cdata = []  # C type: "struct lyd_attr *"

    def get(self, name: str) -> Optional[str]:
        for attr_name, attr_value in self:
            if attr_name == name:
                return attr_value
        return None

    def set(self, name: str, value: str):
        attrs = ffi.new("struct lyd_attr **")
        ret = lib.lyd_new_attr(
            self.parent.cdata,
            ffi.NULL,
            str2c(name),
            str2c(value),
            attrs,
        )
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot create attr")
        self.cdata.append(attrs[0])

    def remove(self, name: str):
        for attr in self.cdata:
            if self._get_attr_name(attr) == name:
                lib.lyd_free_attr_single(self.context.cdata, attr)
                self.cdata.remove(attr)
                break

    def __contains__(self, name: str) -> bool:
        for attr_name, _ in self:
            if attr_name == name:
                return True
        return False

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        for attr in self.cdata:
            name = self._get_attr_name(attr)
            yield (name, c2str(attr.value))

    def __len__(self) -> int:
        return len(self.cdata)

    @staticmethod
    def _get_attr_name(cdata) -> str:
        if cdata.name.prefix != ffi.NULL:
            return f"{c2str(cdata.name.prefix)}:{c2str(cdata.name.name)}"
        return c2str(cdata.name.name)


# -------------------------------------------------------------------------------------
class DNode:
    """
    Data tree node.
    """

    __slots__ = ("context", "cdata", "attributes", "free_func", "__dict__")

    def __init__(self, context: "libyang.Context", cdata):
        """
        :arg context:
            The libyang.Context python object.
        :arg cdata:
            The pointer to the C structure allocated by libyang.so.
        """
        self.context = context
        self.cdata = cdata  # C type: "struct lyd_node *"
        self.attributes = None
        self.free_func = None  # type: Callable[DNode]

    def meta(self):
        ret = {}
        item = self.cdata.meta
        while item != ffi.NULL:
            ret[c2str(item.name)] = c2str(
                lib.lyd_value_get_canonical(
                    self.context.cdata, ffi.addressof(item.value)
                )
            )
            item = item.next
        return ret

    def get_meta(self, name):
        item = self.cdata.meta
        while item != ffi.NULL:
            if c2str(item.name) == name:
                return c2str(
                    lib.lyd_value_get_canonical(
                        self.context.cdata, ffi.addressof(item.value)
                    )
                )
            item = item.next
        return None

    def meta_free(self, name):
        item = self.cdata.meta
        while item != ffi.NULL:
            if c2str(item.name) == name:
                lib.lyd_free_meta_single(item)
                break
            item = item.next

    def new_meta(
        self, name: str, value: str, clear_dflt: bool = False, store_only: bool = False
    ):
        flags = newval_flags(meta_clear_default=clear_dflt, store_only=store_only)
        ret = lib.lyd_new_meta(
            ffi.NULL,
            self.cdata,
            ffi.NULL,
            str2c(name),
            str2c(value),
            flags,
            ffi.NULL,
        )
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot create meta")

    def attrs(self) -> DNodeAttrs:
        if not self.attributes:
            self.attributes = DNodeAttrs(self.context, self)
        return self.attributes

    def add_defaults(
        self,
        no_config: bool = False,
        no_defaults: bool = False,
        no_state: bool = False,
        output: bool = False,
        only_node: bool = False,
        only_module: Optional[Module] = None,
    ):
        flags = implicit_flags(
            no_config=no_config,
            no_defaults=no_defaults,
            no_state=no_state,
            output=output,
        )
        if only_node:
            node_p = ffi.cast("struct lyd_node *", self.cdata)
            ret = lib.lyd_new_implicit_tree(node_p, flags, ffi.NULL)
        else:
            node_p = ffi.new("struct lyd_node **")
            node_p[0] = self.cdata
            if only_module is not None:
                ret = lib.lyd_new_implicit_module(
                    node_p, only_module.cdata, flags, ffi.NULL
                )
            else:
                ret = lib.lyd_new_implicit_all(
                    node_p, self.context.cdata, flags, ffi.NULL
                )

        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot get module")

    def flags(self):
        ret = {"default": False, "when_true": False, "new": False}
        if self.cdata.flags & lib.LYD_DEFAULT:
            ret["default"] = True
        if self.cdata.flags & lib.LYD_WHEN_TRUE:
            ret["when_true"] = True
        if self.cdata.flags & lib.LYD_NEW:
            ret["new"] = True
        return ret

    def set_when(self, value: bool):
        if value:
            self.cdata.flags |= lib.LYD_WHEN_TRUE
        else:
            self.cdata.flags &= ~lib.LYD_WHEN_TRUE

    def new_path(
        self,
        path: str,
        value: str,
        opt_update: bool = False,
        opt_output: bool = False,
        opt_opaq: bool = False,
        opt_bin_value: bool = False,
        opt_canon_value: bool = False,
        opt_store_only: bool = False,
    ):
        flags = newval_flags(
            update=opt_update,
            rpc_output=opt_output,
            opaq=opt_opaq,
            bin_value=opt_bin_value,
            canon_value=opt_canon_value,
            store_only=opt_store_only,
        )
        ret = lib.lyd_new_path(
            self.cdata, ffi.NULL, str2c(path), str2c(value), flags, ffi.NULL
        )
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot get module")

    def insert_child(self, node):
        ret = lib.lyd_insert_child(self.cdata, node.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot insert node")

    def insert_sibling(self, node):
        ret = lib.lyd_insert_sibling(self.cdata, node.cdata, ffi.NULL)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot insert sibling")

    def insert_after(self, node):
        ret = lib.lyd_insert_after(self.cdata, node.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot insert sibling after")

    def insert_before(self, node):
        ret = lib.lyd_insert_before(self.cdata, node.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot insert sibling before")

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
        if ret == lib.LY_SUCCESS:
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

    def eval_xpath(self, xpath: str):
        lbool = ffi.new("ly_bool *")
        ret = lib.lyd_eval_xpath(self.cdata, str2c(xpath), lbool)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot eva xpath: %s", xpath)
        if lbool[0]:
            return True
        return False

    def path(self) -> str:
        return self._get_path(self.cdata)

    def validate(
        self,
        no_state: bool = False,
        validate_present: bool = False,
        rpc: bool = False,
        rpcreply: bool = False,
        notification: bool = False,
    ) -> None:
        dtype = None
        if rpc:
            dtype = DataType.RPC_YANG
        elif rpcreply:
            dtype = DataType.REPLY_YANG
        elif notification:
            dtype = DataType.NOTIF_YANG

        if dtype is None:
            self.validate_all(no_state, validate_present)
        else:
            self.validate_op(dtype)

    def validate_all(
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
    ) -> "DNode":
        flags = diff_flags(with_defaults=with_defaults)
        node_p = ffi.new("struct lyd_node **")
        if no_siblings:
            ret = lib.lyd_diff_tree(self.cdata, other.cdata, flags, node_p)
        else:
            ret = lib.lyd_diff_siblings(self.cdata, other.cdata, flags, node_p)

        if ret != lib.LY_SUCCESS:
            raise self.context.error("diff error")

        if node_p[0] == ffi.NULL:
            return None

        return self.new(self.context, node_p[0])

    def diff_apply(self, diff_node: "DNode") -> None:
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata

        ret = lib.lyd_diff_apply_all(node_p, diff_node.cdata)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("apply diff error")

    def duplicate(
        self,
        with_siblings: bool = False,
        no_meta: bool = False,
        recursive: bool = False,
        with_flags: bool = False,
        with_parents: bool = False,
        parent: Optional["DNode"] = None,
    ) -> "DNode":
        flags = dup_flags(
            no_meta=no_meta,
            recursive=recursive,
            with_flags=with_flags,
            with_parents=with_parents,
        )

        if parent is not None:
            parent = parent.cdata
        else:
            parent = ffi.NULL

        node = ffi.new("struct lyd_node **")
        if with_siblings:
            lib.lyd_dup_siblings(self.cdata, parent, flags, node)
        else:
            lib.lyd_dup_single(self.cdata, parent, flags, node)

        return DNode.new(self.context, node[0])

    def merge_module(
        self,
        source: "DNode",
        defaults: bool = False,
        destruct: bool = False,
        with_flags: bool = False,
    ) -> None:
        flags = merge_flags(defaults=defaults, destruct=destruct, with_flags=with_flags)
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata
        ret = lib.lyd_merge_module(
            node_p, source.cdata, ffi.NULL, ffi.NULL, ffi.NULL, flags
        )
        if ret != lib.LY_SUCCESS:
            raise self.context.error("merge failed")

    def merge(
        self,
        source: "DNode",
        with_siblings: bool = False,
        defaults: bool = False,
        destruct: bool = False,
        with_flags: bool = False,
    ) -> None:
        flags = merge_flags(defaults=defaults, destruct=destruct, with_flags=with_flags)
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata
        if with_siblings:
            ret = lib.lyd_merge_siblings(node_p, source.cdata, flags)
        else:
            ret = lib.lyd_merge_tree(node_p, source.cdata, flags)

        if ret != lib.LY_SUCCESS:
            raise self.context.error("merge failed")

        self.cdata = node_p[0]

    def iter_tree(self) -> Iterator["DNode"]:
        n = next_n = self.cdata
        while n != ffi.NULL:
            yield self.new(self.context, n)

            next_n = lib.lyd_child(n)
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

    def print(
        self,
        fmt: str,
        out_type: IOType,
        out_target: Union[IO, str, None] = None,
        with_siblings: bool = False,
        pretty: bool = True,
        keep_empty_containers: bool = False,
        trim_default_values: bool = False,
        include_implicit_defaults: bool = False,
    ) -> Union[str, bytes]:
        flags = printer_flags(
            pretty=pretty,
            keep_empty_containers=keep_empty_containers,
            trim_default_values=trim_default_values,
            include_implicit_defaults=include_implicit_defaults,
        )
        fmt = data_format(fmt)
        out_data = ffi.new("struct ly_out **")

        if out_type == IOType.FD:
            raise NotImplementedError

        if out_type == IOType.FILE:
            raise NotImplementedError

        if out_type == IOType.FILEPATH:
            raise NotImplementedError

        if out_type != IOType.MEMORY:
            raise ValueError("no input specified")

        buf = ffi.new("char **")
        ret = lib.ly_out_new_memory(buf, 0, out_data)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("failed to initialize output target")

        if with_siblings:
            ret = lib.lyd_print_all(out_data[0], self.cdata, fmt, flags)
        else:
            ret = lib.lyd_print_tree(out_data[0], self.cdata, fmt, flags)

        lib.ly_out_free(out_data[0], ffi.NULL, 0)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("failed to write data")

        return c2str(buf[0], decode=True)

    def print_mem(
        self,
        fmt: str,
        with_siblings: bool = False,
        pretty: bool = True,
        keep_empty_containers: bool = False,
        trim_default_values: bool = False,
        include_implicit_defaults: bool = False,
    ) -> Union[str, bytes]:
        flags = printer_flags(
            with_siblings=with_siblings,
            pretty=pretty,
            keep_empty_containers=keep_empty_containers,
            trim_default_values=trim_default_values,
            include_implicit_defaults=include_implicit_defaults,
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
        pretty: bool = True,
        keep_empty_containers: bool = False,
        trim_default_values: bool = False,
        include_implicit_defaults: bool = False,
    ) -> None:
        flags = printer_flags(
            with_siblings=with_siblings,
            pretty=pretty,
            keep_empty_containers=keep_empty_containers,
            trim_default_values=trim_default_values,
            include_implicit_defaults=include_implicit_defaults,
        )
        fmt = data_format(fmt)
        out = ffi.new("struct ly_out **")
        ret = lib.ly_out_new_fd(fileobj.fileno(), out)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot allocate output data")
        if with_siblings:
            ret = lib.lyd_print_all(out[0], self.cdata, fmt, flags)
        else:
            ret = lib.lyd_print_tree(out[0], self.cdata, fmt, flags)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot print node")

    def should_print(
        self,
        include_implicit_defaults: bool = False,
        trim_default_values: bool = False,
        keep_empty_containers: bool = False,
    ) -> bool:
        """
        Check if a node should be "printed".

        :arg bool include_implicit_defaults:
            Include implicit default nodes.
        :arg bool trim_default_values:
            Exclude nodes with the value equal to their default value.
        :arg bool keep_empty_containers:
            Preserve empty non-presence containers.
        """
        flags = printer_flags(
            include_implicit_defaults=include_implicit_defaults,
            trim_default_values=trim_default_values,
            keep_empty_containers=keep_empty_containers,
        )
        return bool(lib.lyd_node_should_print(self.cdata, flags))

    def print_dict(
        self,
        strip_prefixes: bool = True,
        absolute: bool = True,
        with_siblings: bool = False,
        include_implicit_defaults: bool = False,
        trim_default_values: bool = False,
        keep_empty_containers: bool = False,
    ) -> Dict[str, Any]:
        """
        Convert a DNode object to a python dictionary.

        The format is inspired by the YANG JSON format described in :rfc:`7951` but has
        some differences:

        * ``int64`` and ``uint64`` values are represented by python ``int`` values
          instead of string values.
        * ``decimal64`` values are represented by python ``float`` values instead of
          string values.
        * ``empty`` values are represented by python ``None`` values instead of
          ``[None]`` list instances. To check if an ``empty`` leaf is set in a
          container, you should use the idiomatic ``if "foo" in container:`` construct.

        :arg bool strip_prefixes:
            If True (the default), module prefixes are stripped from dictionary keys. If
            False, dictionary keys are in the form ``<module>:<name>``.
        :arg bool absolute:
            If True (the default), always return a dictionary containing the complete
            tree starting from the root.
        :arg bool with_siblings:
            If True, include the node's siblings.
        :arg bool include_implicit_defaults:
            Include implicit default nodes.
        :arg bool trim_default_values:
            Exclude nodes with the value equal to their default value.
        :arg bool keep_empty_containers:
            Preserve empty non-presence containers.
        """
        flags = printer_flags(
            include_implicit_defaults=include_implicit_defaults,
            trim_default_values=trim_default_values,
            keep_empty_containers=keep_empty_containers,
        )

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
                            keys.append(
                                "%s:%s" % (c2str(child.module.name), c2str(child.name))
                            )
                    child = child.next
                if len(keys) == 1:
                    list_keys_cache[snode] = keys[0]
                else:
                    list_keys_cache[snode] = tuple(keys)

            return KeyedList(key_name=list_keys_cache[snode])

        def _to_dict(node, parent_dic):
            if not lib.lyd_node_should_print(node, flags):
                return
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
                parent_dic[name].append(DLeaf.cdata_leaf_value(node, self.context))
            elif node.schema.nodetype == SNode.LEAF:
                parent_dic[name] = DLeaf.cdata_leaf_value(node, self.context)

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
        rpc: bool = False,
        rpcreply: bool = False,
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
        :arg rpc:
            Data represents RPC or action input parameters.
        :arg rpcreply:
            Data represents RPC or action output parameters.
        """
        return dict_to_dnode(
            dic,
            self.module(),
            parent=self,
            no_state=no_state,
            validate_present=validate_present,
            validate=validate,
            strict=strict,
            rpc=rpc,
            rpcreply=rpcreply,
        )

    def unlink(self, with_siblings: bool = False) -> None:
        if with_siblings:
            lib.lyd_unlink_siblings(self.cdata)
        else:
            lib.lyd_unlink_tree(self.cdata)

    def free_internal(self, with_siblings: bool = True) -> None:
        if with_siblings:
            lib.lyd_free_all(self.cdata)
        else:
            lib.lyd_free_tree(self.cdata)

    def free(self, with_siblings: bool = True) -> None:
        try:
            if self.free_func:
                self.free_func(self)  # pylint: disable=not-callable
            else:
                self.free_internal(with_siblings)
        finally:
            self.cdata = ffi.NULL

    def leafref_link_node_tree(self) -> None:
        """
        Traverse through data tree including root node siblings and adds
        leafrefs links to the given nodes.

        Requires leafref_linking to be set on the libyang context.
        """
        lib.lyd_leafref_link_node_tree(self.cdata)

    def leafref_nodes(self) -> Iterator["DNode"]:
        """
        Gets the leafref links record for given node.

        Requires leafref_linking to be set on the libyang context.
        """
        term_node = ffi.cast("struct lyd_node_term *", self.cdata)
        out = ffi.new("const struct lyd_leafref_links_rec **")
        if lib.lyd_leafref_get_links(term_node, out) != lib.LY_SUCCESS:
            return
        for n in ly_array_iter(out[0].leafref_nodes):
            yield DNode.new(self.context, n)

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
        if not cdata.schema:
            schemas = list(context.find_path(cls._get_path(cdata)))
            if len(schemas) != 1:
                raise LibyangError("Unable to determine schema")
            nodecls = cls.NODETYPE_CLASS.get(schemas[0].nodetype(), None)
        else:
            nodecls = cls.NODETYPE_CLASS.get(cdata.schema.nodetype, None)
        if nodecls is None:
            raise TypeError("node type %s not implemented" % cdata.schema.nodetype)
        return nodecls(context, cdata)

    @staticmethod
    def _get_path(cdata) -> str:
        path = lib.lyd_path(cdata, lib.LYD_PATH_STD, ffi.NULL, 0)
        try:
            return c2str(path)
        finally:
            lib.free(path)


# -------------------------------------------------------------------------------------
@DNode.register(SNode.CONTAINER)
class DContainer(DNode):
    def create_path(
        self,
        path: str,
        value: Any = None,
        rpc_output: bool = False,
        store_only: bool = False,
    ) -> Optional[DNode]:
        return self.context.create_data_path(
            path, parent=self, value=value, rpc_output=rpc_output, store_only=store_only
        )

    def children(self, no_keys=False) -> Iterator[DNode]:
        if no_keys:
            child = lib.lyd_child_no_keys(self.cdata)
        else:
            child = lib.lyd_child(self.cdata)

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
        return DLeaf.cdata_leaf_value(self.cdata, self.context)

    @staticmethod
    def cdata_leaf_value(cdata, context: "libyang.Context" = None) -> Any:
        val = lib.lyd_get_value(cdata)
        if val == ffi.NULL:
            return None

        val = c2str(val)
        if cdata.schema == ffi.NULL:
            # opaq node
            return val

        node_term = ffi.cast("struct lyd_node_term *", cdata)

        # inspired from libyang lyd_value_validate
        val_type = Type(context, node_term.value.realtype, None).base()
        if val_type == Type.UNION:
            val_type = Type(
                context, node_term.value.subvalue.value.realtype, None
            ).base()

        if val_type in Type.STR_TYPES:
            return val
        if val_type in Type.NUM_TYPES:
            return int(val)
        if val_type == Type.BOOL:
            return val == "true"
        if val_type == Type.DEC64:
            return float(val)
        if val_type == Type.EMPTY:
            return None
        return val


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
    def value(self, fmt: str = "xml"):
        anystr = ffi.new("char **", ffi.NULL)
        ret = lib.lyd_any_value_str(self.cdata, anystr)
        if ret != lib.LY_SUCCESS:
            raise self.context.error("cannot get data")
        return c2str(anystr[0])


# -------------------------------------------------------------------------------------
@DNode.register(SNode.ANYDATA)
class DAnydata(DNode):
    def value(self, fmt: str = "xml"):
        anystr = ffi.new("char **", ffi.NULL)
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
    rpc: bool = False,
    rpcreply: bool = False,
    notification: bool = False,
    store_only: bool = False,
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
    :arg rpc:
        Data represents RPC or action input parameters.
    :arg rpcreply:
        Data represents RPC or action output parameters.
    :arg notification:
        Data represents notification parameters.
    :arg store_only:
        Data are being stored regardless of type validation (length, range, pattern, etc.)
    """
    if not dic:
        return None

    if not isinstance(dic, dict):
        raise TypeError("dic argument must be a python dict")
    if not isinstance(module, Module):
        raise TypeError("module argument must be a Module object")
    if parent is not None and not isinstance(parent, DNode):
        raise TypeError("parent argument must be a DNode object or None")

    created = []

    def _create_leaf(_parent, module, name, value, in_rpc_output=False):
        if value is not None:
            if isinstance(value, bool):
                value = str(value).lower()
            elif not isinstance(value, str):
                value = str(value)

        n = ffi.new("struct lyd_node **")
        flags = newval_flags(rpc_output=in_rpc_output, store_only=store_only)
        ret = lib.lyd_new_term(
            _parent,
            module.cdata,
            str2c(name),
            str2c(value),
            flags,
            n,
        )

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
        n = ffi.new("struct lyd_node **")
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
        n = ffi.new("struct lyd_node **")
        flags = newval_flags(rpc_output=in_rpc_output, store_only=store_only)
        ret = lib.lyd_new_list(
            _parent,
            module.cdata,
            str2c(name),
            flags,
            n,
            *[str2c(str(i)) for i in key_values],
        )
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
                        except KeyError as e:
                            raise ValueError("Missing key %s in the list" % (k)) from e

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
                result.root().validate(
                    no_state=no_state,
                    validate_present=validate_present,
                    rpc=rpc,
                    rpcreply=rpcreply,
                    notification=notification,
                )

    except:
        for c in reversed(created):
            lib.lyd_free_tree(c)
        raise

    return result
