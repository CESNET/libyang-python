# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from _libyang import ffi
from _libyang import lib

from .util import c2str
from .util import str2c


#------------------------------------------------------------------------------
class Module:

    def __init__(self, context, module_p):
        self.context = context
        self._module = module_p

    def name(self):
        return c2str(self._module.name)

    def prefix(self):
        return c2str(self._module.prefix)

    def dsc(self):
        return c2str(self._module.dsc)

    def find_path(self, path):
        node_set = ffi.gc(lib.ly_ctx_find_path(self._ctx, str2c(path)),
                          lib.ly_set_free)
        if not node_set:
            raise self.error('cannot find path')

        for i in range(node_set.number):
            yield Node.new(self, node_set.set.s[i])

    def __iter__(self):
        return self.children()

    def children(self, types=None):
        return iter_children(self.context, module=self._module, types=types)

    def __str__(self):
        return self.dump_str()

    def dump_str(self, fmt=lib.LYS_OUT_TREE, path=None):
        buf = ffi.new('char **')
        ret = lib.lys_print_mem(buf, self._module, fmt, str2c(path), 0, 0)
        if ret != 0:
            raise self.context.error('cannot print module')
        return c2str(buf[0])

    def dump_file(self, fileobj, fmt=lib.LYS_OUT_TREE, path=None):
        ret = lib.lys_print_fd(
            fileobj.fileno(), self._module, fmt, str2c(path), 0, 0)
        if ret != 0:
            raise self.context.error('cannot print module')


#------------------------------------------------------------------------------
class Extension:

    def __init__(self, context, ext_p):
        self.context = context
        self._ext = ext_p
        self._def = ext_p['def']

    def name(self):
        return c2str(self._def.name)

    def argument(self):
        return c2str(self._ext.arg_value)

    def module(self):
        module_p = lib.lys_main_module(self._def.module)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)


#------------------------------------------------------------------------------
class Type:

    def __init__(self, context, type_p):
        self.context = context
        self._type = type_p

    def get_builtins(self):
        if self._type.base == lib.LY_TYPE_DER:
            yield from self.parent().get_builtins()
        elif self._type.base == lib.LY_TYPE_LEAFREF:
            lref = self._type.info.lref
            yield from Type(self.context, ffi.addressof(lref.target.type)).get_builtins()
        elif self._type.base == lib.LY_TYPE_UNION:
            t = lib.lys_getnext_union_type(ffi.NULL, self._type)
            while t:
                yield from Type(self.context, t).get_builtins()
                t = lib.lys_getnext_union_type(t, self._type)
        else:  # builtin type
            yield self

    def name(self):
        return c2str(self._type.der.name)

    def dsc(self):
        return c2str(self._type.der.dsc)

    def base(self):
        return self._type.base

    BASENAMES = {
        lib.LY_TYPE_DER: 'derived',
        lib.LY_TYPE_BINARY: 'binary',
        lib.LY_TYPE_BITS: 'bits',
        lib.LY_TYPE_BOOL: 'boolean',
        lib.LY_TYPE_DEC64: 'decimal64',
        lib.LY_TYPE_EMPTY: 'empty',
        lib.LY_TYPE_ENUM: 'enumeration',
        lib.LY_TYPE_IDENT: 'ident',
        lib.LY_TYPE_INST: 'instance-id',
        lib.LY_TYPE_LEAFREF: 'leafref',
        lib.LY_TYPE_STRING: 'string',
        lib.LY_TYPE_UNION: 'union',
        lib.LY_TYPE_INT8: 'int8',
        lib.LY_TYPE_UINT8: 'uint8',
        lib.LY_TYPE_INT16: 'int16',
        lib.LY_TYPE_UINT16: 'uint16',
        lib.LY_TYPE_INT32: 'int32',
        lib.LY_TYPE_UINT32: 'uint32',
        lib.LY_TYPE_INT64: 'int64',
        lib.LY_TYPE_UINT64: 'uint64',
    }

    def basename(self):
        return self.BASENAMES.get(self._type.base, 'unknown')

    def parent(self):
        return Type(self.context, ffi.addressof(self._type.parent.type))

    def module(self):
        module_p = lib.lys_main_module(self._type.der.module)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)

    def extensions(self):
        for i in range(self._type.ext_size):
            yield Extension(self.context, self._type.ext[i])
        for i in range(self._type.der.ext_size):
            yield Extension(self.context, self._type.der.ext[i])

    def get_extension(self, name, prefix=None, arg_value=None):
        ext = lib.lys_find_ext(
            self._type.ext, self._type.ext_size,
            str2c(name), str2c(prefix), str2c(arg_value))
        if not ext and self._type.parent:
            ext = lib.lys_find_ext(
                self._type.parent.ext, self._type.parent.ext_size,
                str2c(name), str2c(prefix), str2c(arg_value))
        if ext:
            return Extension(self.context, ext)
        return None


#------------------------------------------------------------------------------
class Node:

    def __init__(self, context, node_p):
        self.context = context
        self._node = node_p

    def keyword(self):
        return '???'

    def name(self):
        return c2str(self._node.name)

    def dsc(self):
        return c2str(self._node.dsc)

    def module(self):
        module_p = lib.lys_node_module(self._node)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)

    def schema_path(self):
        return c2str(ffi.gc(lib.lys_path(self._node, 0), lib.free))

    def data_path(self):
        return c2str(ffi.gc(lib.lys_data_path_pattern(self._node), lib.free))

    def extensions(self):
        for i in range(self._node.ext_size):
            yield Extension(self.context, self._node.ext[i])

    def get_extension(self, name, prefix=None, arg_value=None):
        ext = lib.lys_find_ext(
            self._node.ext, self._node.ext_size,
            str2c(name), str2c(prefix), str2c(arg_value))
        if ext:
            return Extension(self.context, ext)
        return None

    @staticmethod
    def new(context, node_p):
        nodecls = NODETYPE_CLASS.get(node_p.nodetype, Node)
        return nodecls(context, node_p)


#------------------------------------------------------------------------------
class Leaf(Node):

    def __init__(self, context, node_p):
        super().__init__(context, node_p)
        self._leaf = ffi.cast('struct lys_node_leaf *', node_p)

    def keyword(self):
        return 'leaf'

    def default(self):
        return c2str(self._leaf.dflt)

    def units(self):
        return c2str(self._leaf.units)

    def type(self):
        return Type(self.context, ffi.addressof(self._leaf.type))

    def is_key(self):
        if lib.lys_is_key(self._leaf, ffi.NULL):
            return True
        return False


#------------------------------------------------------------------------------
class LeafList(Node):

    def __init__(self, context, node_p):
        super().__init__(context, node_p)
        self._leaflist = ffi.cast('struct lys_node_leaflist *', node_p)

    def keyword(self):
        return 'leaf-list'

    def units(self):
        return c2str(self._leaf.units)

    def type(self):
        return Type(self.context, ffi.addressof(self._leaflist.type))

    def defaults(self):
        for i in range(self._leaflist.dflt_size):
            yield c2str(self._leaflist.dflt[i])


#------------------------------------------------------------------------------
class Container(Node):

    def __init__(self, context, node_p):
        super().__init__(context, node_p)
        self._container = ffi.cast('struct lys_node_container *', node_p)

    def keyword(self):
        return 'container'

    def presence(self):
        return c2str(self._container.presence)

    def __iter__(self):
        return self.children()

    def children(self, types=None):
        return iter_children(self.context, parent=self._node, types=types)


#------------------------------------------------------------------------------
class List(Node):

    def __init__(self, context, node_p):
        super().__init__(context, node_p)
        self._list = ffi.cast('struct lys_node_list *', node_p)

    def keyword(self):
        return 'list'

    def __iter__(self):
        return self.children()

    def children(self, skip_keys=False, types=None):
        return iter_children(
            self.context, parent=self._node, skip_keys=skip_keys, types=types)

    def keys(self):
        for i in range(self._list.keys_size):
            node = ffi.cast('struct lys_node *', self._list.keys[i])
            yield Leaf(self.context, node)


#------------------------------------------------------------------------------
class Rpc(Node):

    def __init__(self, context, node_p):
        super().__init__(context, node_p)
        self._rpc = ffi.cast('struct lys_node_rpc_action *', node_p)

    def keyword(self):
        return 'rpc'

    def __iter__(self):
        return self.children()

    def children(self, types=None):
        return iter_children(self.context, parent=self._node, types=types)


#------------------------------------------------------------------------------
def iter_children(context, parent=ffi.NULL, module=ffi.NULL, *,
                  skip_keys=False, types=None):
    if types is None:
        types = (lib.LYS_CONTAINER, lib.LYS_LIST, lib.LYS_RPC,
                 lib.LYS_LEAF, lib.LYS_LEAFLIST)

    def _skip(node):
        if node.nodetype not in types:
            return True
        if not skip_keys:
            return False
        if node.nodetype != lib.LYS_LEAF:
            return False
        leaf = ffi.cast('struct lys_node_leaf *', node)
        if lib.lys_is_key(leaf, ffi.NULL):
            return True
        return False

    child = lib.lys_getnext(ffi.NULL, parent, module, 0)
    while child:
        if not _skip(child):
            yield Node.new(context, child)
        child = lib.lys_getnext(child, parent, module, 0)


#------------------------------------------------------------------------------
NODETYPE_CLASS = {
    lib.LYS_CONTAINER: Container,
    lib.LYS_LEAF: Leaf,
    lib.LYS_LEAFLIST: LeafList,
    lib.LYS_LIST: List,
    lib.LYS_RPC: Rpc,
}
