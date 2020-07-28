# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import logging
from typing import IO, Any, Dict, Iterator, Optional, Union

from _libyang import ffi, lib
from .keyed_list import KeyedList
from .schema import Module, SContainer, SLeaf, SLeafList, SList, SNode, SRpc, Type
from .util import LibyangError, c2str, deprecated, str2c


LOG = logging.getLogger(__name__)


# -------------------------------------------------------------------------------------
def printer_flags(
    with_siblings: bool = False,
    pretty: bool = False,
    keep_empty_containers: bool = False,
    trim_default_values: bool = False,
    include_implicit_defaults: bool = False,
) -> int:
    flags = 0
    if with_siblings:
        flags |= lib.LYP_WITHSIBLINGS
    if pretty:
        flags |= lib.LYP_FORMAT
    if keep_empty_containers:
        flags |= lib.LYP_KEEPEMPTYCONT
    if trim_default_values:
        flags |= lib.LYP_WD_TRIM
    if include_implicit_defaults:
        flags |= lib.LYP_WD_ALL
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
        flags |= lib.LYD_PATH_OPT_UPDATE
    if rpc_output:
        flags |= lib.LYD_PATH_OPT_OUTPUT
    if no_parent_ret:
        flags |= lib.LYD_PATH_OPT_NOPARENTRET
    return flags


# -------------------------------------------------------------------------------------
def parser_flags(
    data: bool = False,
    config: bool = False,
    get: bool = False,
    getconfig: bool = False,
    edit: bool = False,
    rpc: bool = False,
    rpcreply: bool = False,
    strict: bool = False,
    trusted: bool = False,
    no_yanglib: bool = False,
    destruct: bool = False,
    no_siblings: bool = False,
    explicit: bool = False,
) -> int:
    if (data, config, get, getconfig, edit, rpc, rpcreply).count(True) > 1:
        raise ValueError(
            "Only one of data, config, get, getconfig, edit, rpc, rpcreply can be True"
        )
    flags = 0
    if data:
        flags |= lib.LYD_OPT_DATA
    if config:
        flags |= lib.LYD_OPT_CONFIG
    if get:
        flags |= lib.LYD_OPT_GET
    if getconfig:
        flags |= lib.LYD_OPT_GETCONFIG
    if edit:
        flags |= lib.LYD_OPT_EDIT
    if rpc:
        flags |= lib.LYD_OPT_RPC
    if rpcreply:
        flags |= lib.LYD_OPT_RPCREPLY
    if strict:
        flags |= lib.LYD_OPT_STRICT
    if trusted:
        flags |= lib.LYD_OPT_TRUSTED
    if no_yanglib:
        flags |= lib.LYD_OPT_DATA_NO_YANGLIB
    if destruct:
        flags |= lib.LYD_OPT_DESTRUCT
    if no_siblings:
        flags |= lib.LYD_OPT_NOSIBLINGS
    if explicit:
        flags |= lib.LYD_OPT_EXPLICIT
    return flags


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

    @property
    def _node(self):
        deprecated("_node", "cdata", "2.0.0")
        return self.cdata

    def name(self) -> str:
        return c2str(self.cdata.schema.name)

    def module(self) -> Module:
        mod = lib.lyd_node_module(self.cdata)
        if not mod:
            raise self.context.error("cannot get module")
        return Module(self.context, mod)

    def schema(self) -> SNode:
        return SNode.new(self.context, self.cdata.schema)

    def parent(self) -> Optional["DNode"]:
        if not self.cdata.parent:
            return None
        return self.new(self.context, self.cdata.parent)

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

    def find_one(self, xpath: str) -> Optional["DNode"]:
        try:
            return next(self.find_all(xpath))
        except StopIteration:
            return None

    def find_all(self, xpath: str) -> Iterator["DNode"]:
        node_set = lib.lyd_find_path(self.cdata, str2c(xpath))
        if not node_set:
            raise self.context.error("cannot find path")
        try:
            for i in range(node_set.number):
                yield DNode.new(self.context, node_set.d[i])
        finally:
            lib.ly_set_free(node_set)

    def path(self) -> str:
        path = lib.lyd_path(self.cdata)
        try:
            return c2str(path)
        finally:
            lib.free(path)

    def validate(
        self,
        data: bool = False,
        config: bool = False,
        get: bool = False,
        getconfig: bool = False,
        edit: bool = False,
        rpc: bool = False,
        rpcreply: bool = False,
        no_yanglib: bool = False,
    ) -> None:
        if self.cdata.parent:
            raise self.context.error("validation is only supported on top-level nodes")
        flags = parser_flags(
            data=data,
            config=config,
            get=get,
            getconfig=getconfig,
            edit=edit,
            rpc=rpc,
            rpcreply=rpcreply,
            no_yanglib=no_yanglib,
        )
        node_p = ffi.new("struct lyd_node **")
        node_p[0] = self.cdata
        ret = lib.lyd_validate(node_p, flags, ffi.NULL)
        if ret != 0:
            raise self.context.error("validation failed")

    def merge(
        self,
        source: "DNode",
        destruct: bool = False,
        no_siblings: bool = False,
        explicit: bool = False,
    ) -> None:
        flags = parser_flags(
            destruct=destruct, no_siblings=no_siblings, explicit=explicit
        )
        ret = lib.lyd_merge(self.cdata, source.cdata, flags)
        if ret != 0:
            raise self.context.error("merge failed")

    def print_mem(
        self,
        fmt: str,
        with_siblings: bool = False,
        pretty: bool = False,
        include_implicit_defaults: bool = False,
        trim_default_values: bool = False,
        keep_empty_containers: bool = False,
    ) -> Union[str, bytes]:
        flags = printer_flags(
            with_siblings=with_siblings,
            pretty=pretty,
            include_implicit_defaults=include_implicit_defaults,
            trim_default_values=trim_default_values,
            keep_empty_containers=keep_empty_containers,
        )
        buf = ffi.new("char **")
        fmt = data_format(fmt)
        ret = lib.lyd_print_mem(buf, self.cdata, fmt, flags)
        if ret != 0:
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
        pretty: bool = False,
        include_implicit_defaults: bool = False,
        trim_default_values: bool = False,
        keep_empty_containers: bool = False,
    ) -> None:
        flags = printer_flags(
            with_siblings=with_siblings,
            pretty=pretty,
            include_implicit_defaults=include_implicit_defaults,
            trim_default_values=trim_default_values,
            keep_empty_containers=keep_empty_containers,
        )
        fmt = data_format(fmt)
        ret = lib.lyd_print_fd(fileobj.fileno(), self.cdata, fmt, flags)
        if ret != 0:
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
                    mod = lib.lyd_node_module(node)
                    name = "%s:%s" % (c2str(mod.name), c2str(node.schema.name))
                name_cache[node.schema] = name
            return name

        list_keys_cache = {}

        def _init_yang_list(snode):
            if snode.flags & lib.LYS_USERORDERED:
                return []  # ordered list, return an empty builtin list

            # unordered lists
            if snode.nodetype == SNode.LEAFLIST:
                return KeyedList(key_name=None)

            if snode not in list_keys_cache:
                list_snode = ffi.cast("struct lys_node_list *", snode)
                keys = []
                for i in range(list_snode.keys_size):
                    key = ffi.cast("struct lys_node *", list_snode.keys[i])
                    keys.append(c2str(key.name))
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
                child = node.child
                while child:
                    _to_dict(child, list_element)
                    child = child.next
                if name not in parent_dic:
                    parent_dic[name] = _init_yang_list(node.schema)
                parent_dic[name].append(list_element)
            elif node.schema.nodetype & (SNode.CONTAINER | SNode.RPC | SNode.ACTION):
                container = {}
                child = node.child
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
    ) -> Optional["DNode"]:
        """
        Merge a python dictionary into this node. The returned value is the first
        created node.

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
            Instead of ignoring (with a warning message) data without schema
            definition, raise an error.
        :arg no_yanglib:
            Ignore (possibly) missing ietf-yang-library data. Applicable only with
            data=True.
        :arg validate:
            If False, do not validate the modified tree before returning. The validation
            is performed on the top of the modified data tree.
        """
        return dict_to_dnode(
            dic,
            self.module(),
            parent=self,
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

    def free(self, with_siblings: bool = True) -> None:
        try:
            if with_siblings:
                lib.lyd_free_withsiblings(self.cdata)
            else:
                lib.lyd_free(self.cdata)
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
            raise NotImplementedError(
                "node type %s not implemented" % cdata.schema.nodetype
            )
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
        child = self.cdata.child
        while child:
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
    @property
    def _leaf(self):
        deprecated("_leaf", "cdata_leaf", "2.0.0")
        return ffi.cast("struct lyd_node_leaf_list *", self.cdata)

    def value(self) -> Any:
        return DLeaf.cdata_leaf_value(self.cdata)

    @staticmethod
    def cdata_leaf_value(cdata) -> Any:
        cdata = ffi.cast("struct lyd_node_leaf_list *", cdata)
        val_type = cdata.value_type
        if val_type in Type.STR_TYPES:
            return c2str(cdata.value_str)
        if val_type in Type.NUM_TYPES:
            return int(c2str(cdata.value_str))
        if val_type == Type.BOOL:
            return bool(cdata.value.bln)
        if val_type == Type.DEC64:
            return lib.lyd_dec64_to_double(ffi.cast("struct lyd_node *", cdata))
        if val_type == Type.LEAFREF:
            return DLeaf.cdata_leaf_value(cdata.value.leafref)
        return None


# -------------------------------------------------------------------------------------
@DNode.register(SNode.LEAFLIST)
class DLeafList(DLeaf):
    pass


# -------------------------------------------------------------------------------------
def dict_to_dnode(
    dic: Dict[str, Any],
    module: Module,
    parent: Optional[DNode] = None,
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
    :arg data:
        Complete datastore content with configuration as well as state data. To handle
        possibly missing (but by default required) ietf-yang-library data, use
        no_yanglib=True.
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
        If False, do not validate the modified tree before returning. The validation is
        performed on the top of the data tree.
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
        if in_rpc_output:
            n = lib.lyd_new_output_leaf(
                _parent, module.cdata, str2c(name), str2c(value)
            )
        else:
            n = lib.lyd_new_leaf(_parent, module.cdata, str2c(name), str2c(value))
        if not n:
            if _parent:
                parent_path = repr(DNode.new(module.context, _parent).path())
            else:
                parent_path = "module %r" % module.name()
            raise module.context.error(
                "failed to create leaf %r as a child of %s", name, parent_path
            )
        created.append(n)

    def _create_container(_parent, module, name, in_rpc_output=False):
        if in_rpc_output:
            n = lib.lyd_new_output(_parent, module.cdata, str2c(name))
        else:
            n = lib.lyd_new(_parent, module.cdata, str2c(name))
        if not n:
            if _parent:
                parent_path = repr(DNode.new(module.context, _parent).path())
            else:
                parent_path = "module %r" % module.name()
            raise module.context.error(
                "failed to create container/list/rpc %r as a child of %s",
                name,
                parent_path,
            )
        created.append(n)
        return n

    schema_cache = {}

    def _find_schema(schema_parent, name, prefix):
        cache_key = (schema_parent.cdata, name, prefix)
        snode, module = schema_cache.get(cache_key, (None, None))
        if snode is not None:
            return snode, module
        if isinstance(schema_parent, SRpc):
            if rpc:
                schema_parent = schema_parent.input()
            elif rpcreply:
                schema_parent = schema_parent.output()
            else:
                raise ValueError("rpc or rpcreply must be specified")
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
                prefix, name = name.split(":")
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
                for v in value:
                    if not isinstance(v, dict):
                        raise TypeError(
                            "%s: list element is not a dict: %r"
                            % (_schema.schema_path(), v)
                        )
                    n = _create_container(_parent, module, name, in_rpc_output)
                    _to_dnode(v, s, n, in_rpc_output)

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
                    data=data,
                    config=config,
                    get=get,
                    getconfig=getconfig,
                    edit=edit,
                    rpc=rpc,
                    rpcreply=rpcreply,
                    no_yanglib=no_yanglib,
                )
    except:
        for c in reversed(created):
            lib.lyd_free(c)
        raise

    return result
