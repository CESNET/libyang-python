# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

from _libyang import ffi
from _libyang import lib

from .schema import Module
from .schema import SContainer
from .schema import SLeaf
from .schema import SLeafList
from .schema import SList
from .schema import SNode
from .schema import SRpc
from .schema import Type
from .util import c2str
from .util import str2c


#------------------------------------------------------------------------------
class PrintFmt:  # TODO: use enum when dropping python2 support
    XML = lib.LYD_XML
    JSON = lib.LYD_JSON
    LYB = lib.LYD_LYB


#------------------------------------------------------------------------------
class PrintOpt:  # TODO: use enum when dropping python2 support
    PRETTY = lib.LYP_FORMAT


#------------------------------------------------------------------------------
class PathOpt:  # TODO: use enum when dropping python2 support
    UPDATE = lib.LYD_PATH_OPT_UPDATE
    OUTPUT = lib.LYD_PATH_OPT_OUTPUT
    NOPARENTRET = lib.LYD_PATH_OPT_NOPARENTRET


#------------------------------------------------------------------------------
class ParserOpt:  # TODO: use enum when dropping python2 support
    DATA = lib.LYD_OPT_DATA
    CONFIG = lib.LYD_OPT_CONFIG
    STRICT = lib.LYD_OPT_STRICT
    TRUSTED = lib.LYD_OPT_TRUSTED
    NO_YANGLIB = lib.LYD_OPT_DATA_NO_YANGLIB


#------------------------------------------------------------------------------
class DNode(object):
    """
    Data tree node.
    """
    def __init__(self, context, node_p, autofree=False):
        """
        :arg Context context:
            The libyang.Context python object.
        :arg struct lyd_node * node_p:
            The pointer to the C structure allocated by libyang.so.
        :arg bool autofree:
            If True, automatically call lyd_free_withsiblings when the last
            reference to this object is lost.
        """
        self.context = context
        self._node = ffi.cast('struct lyd_node *', node_p)
        if autofree:
            self._node = ffi.gc(self._node, lib.lyd_free_withsiblings)

    def name(self):
        return c2str(self._node.schema.name)

    def module(self):
        mod = lib.lyd_node_module(self._node)
        if not mod:
            raise self.context.error('cannot get module')
        return Module(self.context, mod)

    def schema(self):
        return SNode.new(self.context, self._node.schema)

    def default(self):
        return bool(self._node.dflt)

    def parent(self):
        if not self._node.parent:
            return None
        return self.new(self.context, self._node.parent)

    def find_one(self, xpath):
        try:
            return next(self.find_all(xpath))
        except StopIteration:
            return None

    def find_all(self, xpath):
        node_set = lib.lyd_find_path(self._node, str2c(xpath))
        if not node_set:
            raise self.context.error('cannot find path: %s', xpath)
        try:
            for i in range(node_set.number):
                yield DNode.new(self.context, node_set.d[i])
        finally:
            lib.ly_set_free(node_set)

    def path(self):
        path = lib.lyd_path(self._node)
        try:
            return c2str(path)
        finally:
            lib.free(path)

    def validate(self, flags=0):
        node_p = ffi.new('struct lyd_node **')
        node_p[0] = self._node
        ret = lib.lyd_validate(node_p, flags, ffi.NULL)
        if ret != 0:
            self.context.error('validation failed')

    def dump_str(self, fmt=PrintFmt.JSON, flags=0):
        buf = ffi.new('char **')
        ret = lib.lyd_print_mem(buf, self._node, fmt, flags)
        if ret != 0:
            raise self.context.error('cannot print node')
        try:
            return c2str(buf[0])
        finally:
            lib.free(buf[0])

    def dump_file(self, fileobj, fmt=PrintFmt.JSON, flags=0):
        ret = lib.lyd_print_fd(fileobj.fileno(), self._node, fmt, flags)
        if ret != 0:
            raise self.context.error('cannot print node')

    def free(self, with_siblings=True):
        try:
            ffi.gc(self._node, None)  # disable automatic gc
        except TypeError:
            pass
        try:
            if with_siblings:
                lib.lyd_free_withsiblings(self._node)
            else:
                lib.lyd_free(self._node)
        finally:
            self._node = None

    def __repr__(self):
        cls = self.__class__
        return '<%s.%s: %s>' % (cls.__module__, cls.__name__, str(self))

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
    def new(cls, context, node_p, autofree=False):
        node_p = ffi.cast('struct lyd_node *', node_p)
        nodecls = cls.NODETYPE_CLASS.get(node_p.schema.nodetype, DNode)
        return nodecls(context, node_p, autofree=autofree)


#------------------------------------------------------------------------------
@DNode.register(SNode.CONTAINER)
class DContainer(DNode):

    def create_path(self, path, value=None, flags=0):
        return self.context.create_data_path(
            path, parent=self, value=value, flags=flags)

    def children(self):
        child = self._node.child
        while child:
            yield DNode.new(self.context, child)
            child = child.next

    def __iter__(self):
        return self.children()


#------------------------------------------------------------------------------
@DNode.register(SNode.RPC)
class DRpc(DContainer):
    pass


#------------------------------------------------------------------------------
@DNode.register(SNode.LIST)
class DList(DContainer):
    pass


#------------------------------------------------------------------------------
@DNode.register(SNode.LEAF)
class DLeaf(DNode):

    def __init__(self, context, node_p, autofree=False):
        DNode.__init__(self, context, node_p, autofree=autofree)
        self._leaf = ffi.cast('struct lyd_node_leaf_list *', node_p)

    def set_value(self, new_val):
        if new_val is not None:
            if isinstance(new_val, bool):
                new_val = str(new_val).lower()
            elif not isinstance(new_val, str):
                new_val = str(new_val)
        if lib.lyd_change_leaf(self._leaf, str2c(new_val)) < 0:
            raise self.context.error('failed to change leaf value')

    def value(self):
        if self._leaf.value_type == Type.EMPTY:
            return None
        if self._leaf.value_type in Type.NUM_TYPES:
            return int(c2str(self._leaf.value_str))
        if self._leaf.value_type in (
                Type.STRING, Type.BINARY, Type.ENUM, Type.IDENT, Type.BITS):
            return c2str(self._leaf.value_str)
        if self._leaf.value_type == Type.DEC64:
            return lib.lyd_dec64_to_double(self._node)
        if self._leaf.value_type == Type.LEAFREF:
            referenced = DNode.new(self.context, self._leaf.value.leafref)
            return referenced.value()
        if self._leaf.value_type == Type.BOOL:
            return bool(self._leaf.value.bln)


#------------------------------------------------------------------------------
@DNode.register(SNode.LEAFLIST)
class DLeafList(DLeaf):
    pass


#------------------------------------------------------------------------------
def dnode_to_dict(dnode, strip_prefixes=True):
    """
    Convert a DNode object to a python dictionary.

    :arg DNode dnode:
        The data node to convert.
    :arg bool strip_prefixes:
        If True (the default), module prefixes are stripped from dictionary
        keys. If False, dictionary keys are in the form ``<module>:<name>``.
    """
    def _to_dict(node, parent_dic):
        if strip_prefixes:
            name = node.name()
        else:
            name = '%s:%s' % (node.module().name(), node.name())
        if isinstance(node, DList):
            list_element = {}
            for child in node:
                _to_dict(child, list_element)
            parent_dic.setdefault(name, []).append(list_element)
        elif isinstance(node, (DContainer, DRpc)):
            container = {}
            for child in node:
                _to_dict(child, container)
            parent_dic[name] = container
        elif isinstance(node, DLeafList):
            parent_dic.setdefault(name, []).append(node.value())
        elif isinstance(node, DLeaf):
            parent_dic[name] = node.value()

    dic = {}
    _to_dict(dnode, dic)
    return dic


#------------------------------------------------------------------------------
def dict_to_dnode(dic, schema, parent=None, rpc_input=False, rpc_output=False):
    """
    Convert a python dictionary to a DNode object given a YANG schema object.
    The returned value is always a top-level data node (i.e.: without parent).

    :arg dict dic:
        The python dictionary to convert.
    :arg SNode or Module schema:
        The libyang schema object associated with the dictionary. It must be
        at the same "level" than the dictionary (i.e.: direct children names of
        the schema object must be keys in the dictionary).
    :arg DNode parent:
        Optional parent to update. If not specified a new top-level DNode will
        be created.
    :arg bool rpc_input:
        If True, expect schema to be a SRpc object and dic will be parsed
        by looking in the rpc input nodes.
    :arg bool rpc_output:
        If True, expect schema to be a SRpc object and dic will be parsed
        by looking in the rpc output nodes.
    """
    if not dic:
        return parent

    flags = 0
    if rpc_output:
        flags |= PathOpt.OUTPUT

    # XXX: ugly, required for python2. Cannot use nonlocal keyword
    _parent = [parent]

    def _to_dnode(_dic, _schema, key=()):
        if isinstance(_schema, SRpc):
            if rpc_input:
                _schema = _schema.input()
            elif rpc_output:
                _schema = _schema.output()
            else:
                raise ValueError('rpc_input or rpc_output must be specified')
        if not _schema:
            return
        for s in _schema:
            name = s.name()
            if name not in _dic:
                name = s.fullname()
                if name not in _dic:
                    continue
            d = _dic[name]
            if isinstance(s, SContainer):
                if s.presence():
                    dnode = s.context.create_data_path(
                        s.data_path() % key, parent=_parent[0], flags=flags)
                    if _parent[0] is None:
                        _parent[0] = dnode
                _to_dnode(d, s, key)
            elif isinstance(s, SList):
                for element in d:
                    next_key = tuple(
                        element.get(k.name(), element.get(k.fullname()))
                        for k in s.keys())
                    _to_dnode(element, s, key + next_key)
            elif isinstance(s, SLeafList):
                for element in d:
                    dnode = s.context.create_data_path(
                        s.data_path() % key, parent=_parent[0],
                        value=element, flags=flags)
                    if _parent[0] is None:
                        _parent[0] = dnode
            elif isinstance(s, SLeaf):
                dnode = s.context.create_data_path(
                    s.data_path() % key, parent=_parent[0], value=d, flags=flags)
                if _parent[0] is None:
                    _parent[0] = dnode

    _to_dnode(dic, schema)

    # XXX: ugly, required for python2 support
    parent = _parent[0]

    if parent is not None:
        # go back to the root of the created tree
        while parent.parent() is not None:
            parent = parent.parent()

    return parent
