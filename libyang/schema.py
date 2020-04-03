# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

from _libyang import ffi
from _libyang import lib

from .util import c2str
from .util import str2c


#------------------------------------------------------------------------------
class Module(object):

    def __init__(self, context, module_p):
        self.context = context
        self._module = module_p

    def name(self):
        return c2str(self._module.name)

    def prefix(self):
        return c2str(self._module.prefix)

    def description(self):
        return c2str(self._module.dsc)

    def filepath(self):
        return c2str(self._module.filepath)

    def feature_enable(self, name):
        ret = lib.lys_features_enable(self._module, str2c(name))
        if ret != 0:
            raise self.context.error('no such feature: %r' % name)

    def feature_enable_all(self):
        self.feature_enable('*')

    def feature_disable(self, name):
        ret = lib.lys_features_disable(self._module, str2c(name))
        if ret != 0:
            raise self.context.error('no such feature: %r' % name)

    def feature_disable_all(self):
        self.feature_disable('*')

    def feature_state(self, name):
        ret = lib.lys_features_state(self._module, str2c(name))
        if ret < 0:
            raise self.context.error('no such feature: %r' % name)
        return bool(ret)

    def features(self):
        for i in range(self._module.features_size):
            yield Feature(self.context, self._module.features[i])

    def get_feature(self, name):
        for f in self.features():
            if f.name() == name:
                return f
        raise self.context.error('no such feature: %r' % name)

    def revisions(self):
        for i in range(self._module.rev_size):
            yield Revision(self.context, self._module.rev[i])

    def __iter__(self):
        return self.children()

    def children(self, types=None):
        return iter_children(self.context, self._module, types=types)

    def __str__(self):
        return self.dump_str()

    def dump_str(self, fmt=lib.LYS_OUT_TREE, path=None):
        buf = ffi.new('char **')
        ret = lib.lys_print_mem(buf, self._module, fmt, str2c(path), 0, 0)
        if ret != 0:
            raise self.context.error('cannot print module')
        try:
            return c2str(buf[0])
        finally:
            lib.free(buf[0])

    def dump_file(self, fileobj, fmt=lib.LYS_OUT_TREE, path=None):
        ret = lib.lys_print_fd(
            fileobj.fileno(), self._module, fmt, str2c(path), 0, 0)
        if ret != 0:
            raise self.context.error('cannot print module')


#------------------------------------------------------------------------------
class Revision(object):

    def __init__(self, context, rev_p):
        self.context = context
        self._rev = rev_p

    def date(self):
        return c2str(self._rev.date)

    def description(self):
        return c2str(self._rev.dsc)

    def reference(self):
        return c2str(self._rev.ref)

    def extensions(self):
        for i in range(self._rev.ext_size):
            yield Extension(self.context, self._rev.ext[i])

    def get_extension(self, name, prefix=None, arg_value=None):
        ext = lib.lypy_find_ext(
            self._rev.ext, self._rev.ext_size,
            str2c(name), str2c(prefix), str2c(arg_value))
        if ext:
            return Extension(self.context, ext)
        return None

    def __repr__(self):
        cls = self.__class__
        return '<%s.%s: %s>' % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.date()


#------------------------------------------------------------------------------
class Extension(object):

    def __init__(self, context, ext_p):
        self.context = context
        self._ext = ext_p
        self._def = getattr(ext_p, 'def')

    def name(self):
        return c2str(self._def.name)

    def argument(self):
        return c2str(self._ext.arg_value)

    def module(self):
        module_p = lib.lys_main_module(self._def.module)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)

    def __repr__(self):
        cls = self.__class__
        return '<%s.%s: %s>' % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()


#------------------------------------------------------------------------------
class Type(object):

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
        DER: 'derived',
        BINARY: 'binary',
        BITS: 'bits',
        BOOL: 'boolean',
        DEC64: 'decimal64',
        EMPTY: 'empty',
        ENUM: 'enumeration',
        IDENT: 'identityref',
        INST: 'instance-id',
        LEAFREF: 'leafref',
        STRING: 'string',
        UNION: 'union',
        INT8: 'int8',
        UINT8: 'uint8',
        INT16: 'int16',
        UINT16: 'uint16',
        INT32: 'int32',
        UINT32: 'uint32',
        INT64: 'int64',
        UINT64: 'uint64',
    }

    def __init__(self, context, type_p):
        self.context = context
        self._type = type_p

    def get_bases(self):
        if self._type.base == lib.LY_TYPE_DER:
            for b in self.derived_type().get_bases():
                yield b
        elif self._type.base == lib.LY_TYPE_LEAFREF:
            for b in self.leafref_type().get_bases():
                yield b
        elif self._type.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                for b in t.get_bases():
                    yield b
        else:  # builtin type
            yield self

    def name(self):
        if self._type.der:
            return c2str(self._type.der.name)
        return self.basename()

    def description(self):
        if self._type.der:
            return c2str(self._type.der.dsc)
        return None

    def base(self):
        return self._type.base

    def bases(self):
        for b in self.get_bases():
            yield b.base()

    def basename(self):
        return self.BASENAMES.get(self._type.base, 'unknown')

    def basenames(self):
        for b in self.get_bases():
            yield b.basename()

    def derived_type(self):
        if not self._type.der:
            return None
        return Type(self.context, ffi.addressof(self._type.der.type))

    def leafref_type(self):
        if self._type.base != self.LEAFREF:
            return None
        lref = self._type.info.lref
        return Type(self.context, ffi.addressof(lref.target.type))

    def union_types(self):
        if self._type.base != self.UNION:
            return
        t = self._type
        while t.info.uni.count == 0:
            t = ffi.addressof(t.der.type)
        for i in range(t.info.uni.count):
            yield Type(self.context, t.info.uni.types[i])

    def enums(self):
        if self._type.base != self.ENUM:
            return
        t = self._type
        while t.info.enums.count == 0:
            t = ffi.addressof(t.der.type)
        for i in range(t.info.enums.count):
            e = t.info.enums.enm[i]
            yield c2str(e.name), c2str(e.dsc)

    def all_enums(self):
        for b in self.get_bases():
            for e in b.enums():
                yield e

    def bits(self):
        if self._type.base != self.BITS:
            return
        t = self._type
        while t.info.bits.count == 0:
            t = ffi.addressof(t.der.type)
        for i in range(t.info.bits.count):
            b = t.info.bits.bit[i]
            yield c2str(b.name), c2str(b.dsc)

    def all_bits(self):
        for b in self.get_bases():
            for bb in b.bits():
                yield bb

    NUM_TYPES = frozenset(
        (INT8, INT16, INT32, INT64, UINT8, UINT16, UINT32, UINT64))

    def range(self):
        if self._type.base in self.NUM_TYPES and self._type.info.num.range:
            return c2str(self._type.info.num.range.expr)
        elif self._type.base == self.DEC64 and self._type.info.dec64.range:
            return c2str(self._type.info.dec64.range.expr)
        elif self._type.der:
            return self.derived_type().range()
        return None

    def all_ranges(self):
        if self._type.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                for r in t.all_ranges():
                    yield r
        else:
            rng = self.range()
            if rng is not None:
                yield rng

    def length(self):
        if self._type.base == self.STRING and self._type.info.str.length:
            return c2str(self._type.info.str.length.expr)
        elif self._type.base == self.BINARY and self._type.info.binary.length:
            return c2str(self._type.info.binary.length.expr)
        elif self._type.der:
            return self.derived_type().length()
        return None

    def all_lengths(self):
        if self._type.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                for l in t.all_lengths():
                    yield l
        else:
            length = self.length()
            if length is not None:
                yield length

    def patterns(self):
        if self._type.base != self.STRING:
            return
        for i in range(self._type.info.str.pat_count):
            p = self._type.info.str.patterns[i]
            if not p:
                continue
            # in case of pattern restriction, the first byte has a special
            # meaning: 0x06 (ACK) for regular match and 0x15 (NACK) for
            # invert-match
            invert_match = p.expr[0] == 0x15
            # yield tuples like:
            #     ('[a-zA-Z_][a-zA-Z0-9\-_.]*', False)
            #     ('[xX][mM][lL].*', True)
            yield c2str(p.expr + 1), invert_match
        if self._type.der:
            for p in self.derived_type().patterns():
                yield p

    def all_patterns(self):
        if self._type.base == lib.LY_TYPE_UNION:
            for t in self.union_types():
                for p in t.all_patterns():
                    yield p
        else:
            for p in self.patterns():
                yield p

    def module(self):
        module_p = lib.lys_main_module(self._type.der.module)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)

    def extensions(self):
        for i in range(self._type.ext_size):
            yield Extension(self.context, self._type.ext[i])
        if self._type.parent:
            for i in range(self._type.parent.ext_size):
                yield Extension(self.context, self._type.parent.ext[i])

    def get_extension(self, name, prefix=None, arg_value=None):
        ext = lib.lypy_find_ext(
            self._type.ext, self._type.ext_size,
            str2c(name), str2c(prefix), str2c(arg_value))
        if not ext and self._type.parent:
            ext = lib.lypy_find_ext(
                self._type.parent.ext, self._type.parent.ext_size,
                str2c(name), str2c(prefix), str2c(arg_value))
        if ext:
            return Extension(self.context, ext)
        return None

    def __repr__(self):
        cls = self.__class__
        return '<%s.%s: %s>' % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()


#------------------------------------------------------------------------------
class Feature(object):

    def __init__(self, context, feature_p):
        self.context = context
        self._feature = feature_p

    def name(self):
        return c2str(self._feature.name)

    def description(self):
        return c2str(self._feature.dsc)

    def reference(self):
        return c2str(self._feature.ref)

    def state(self):
        return bool(self._feature.flags & lib.LYS_FENABLED)

    def deprecated(self):
        return bool(self._feature.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self):
        return bool(self._feature.flags & lib.LYS_STATUS_OBSLT)

    def if_features(self):
        for i in range(self._feature.iffeature_size):
            yield IfFeatureExpr(self.context, self._feature.iffeature[i])

    def module(self):
        module_p = lib.lys_main_module(self._feature.module)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)

    def __str__(self):
        return self.name()


#------------------------------------------------------------------------------
class IfFeatureExpr(object):

    def __init__(self, context, iffeature_p):
        self.context = context
        self._iffeature = iffeature_p

    def _get_operator(self, position):
        # the ->exp field is a 2bit array of operator values stored under
        # a uint8_t C array.
        mask = 0x3  # 2bits mask
        shift = 2 * (position % 4)
        item = self._iffeature.expr[position // 4]
        result = item & (mask << shift)
        return result >> shift

    def _operands(self):
        op_index = 0
        ft_index = 0
        expected = 1
        while expected > 0:
            operator = self._get_operator(op_index)
            op_index += 1
            if operator == lib.LYS_IFF_F:
                yield IfFeature(self.context, self._iffeature.features[ft_index])
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

    def tree(self):
        def _tree(operands):
            op = next(operands)
            if op is IfNotFeature:
                return op(self.context, _tree(operands))
            elif op in (IfAndFeatures, IfOrFeatures):
                return op(self.context, _tree(operands), _tree(operands))
            else:
                return op
        return _tree(self._operands())

    def dump(self):
        return self.tree().dump()

    def __str__(self):
        return str(self.tree()).strip('()')


#------------------------------------------------------------------------------
class IfFeatureExprTree(object):

    def dump(self, indent=0):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


#------------------------------------------------------------------------------
class IfFeature(IfFeatureExprTree):

    def __init__(self, context, feature_p):
        self.context = context
        self._feature = feature_p

    def feature(self):
        return Feature(self.context, self._feature)

    def dump(self, indent=0):
        feat = self.feature()
        return '%s%s [%s]\n' % (' ' * indent, feat.name(), feat.description())

    def __str__(self):
        return self.feature().name()


#------------------------------------------------------------------------------
class IfNotFeature(IfFeatureExprTree):

    def __init__(self, context, child):
        self.context = context
        self.child = child

    def dump(self, indent=0):
        return ' ' * indent + 'NOT\n' + self.child.dump(indent + 1)

    def __str__(self):
        return 'NOT %s' % self.child


#------------------------------------------------------------------------------
class IfAndFeatures(IfFeatureExprTree):

    def __init__(self, context, a, b):
        self.context = context
        self.a = a
        self.b = b

    def dump(self, indent=0):
        s = ' ' * indent + 'AND\n'
        s += self.a.dump(indent + 1)
        s += self.b.dump(indent + 1)
        return s

    def __str__(self):
        return '%s AND %s' % (self.a, self.b)


#------------------------------------------------------------------------------
class IfOrFeatures(IfFeatureExprTree):

    def __init__(self, context, a, b):
        self.context = context
        self.a = a
        self.b = b

    def dump(self, indent=0):
        s = ' ' * indent + 'OR\n'
        s += self.a.dump(indent + 1)
        s += self.b.dump(indent + 1)
        return s

    def __str__(self):
        return '(%s OR %s)' % (self.a, self.b)


#------------------------------------------------------------------------------
class SNode(object):

    CONTAINER = lib.LYS_CONTAINER
    LEAF = lib.LYS_LEAF
    LEAFLIST = lib.LYS_LEAFLIST
    LIST = lib.LYS_LIST
    RPC = lib.LYS_RPC
    INPUT = lib.LYS_INPUT
    OUTPUT = lib.LYS_OUTPUT
    KEYWORDS = {
        CONTAINER: 'container',
        LEAF: 'leaf',
        LEAFLIST: 'leaf-list',
        LIST: 'list',
        RPC: 'rpc',
        INPUT: 'input',
        OUTPUT: 'output',
    }

    def __init__(self, context, node_p):
        self.context = context
        self._node = node_p

    def nodetype(self):
        return self._node.nodetype

    def keyword(self):
        return self.KEYWORDS.get(self._node.nodetype, '???')

    def name(self):
        return c2str(self._node.name)

    def fullname(self):
        try:
            s = lib.lypy_node_fullname(self._node)
            return c2str(s)
        finally:
            lib.free(s)

    def description(self):
        return c2str(self._node.dsc)

    def config_set(self):
        return bool(self._node.flags & lib.LYS_CONFIG_SET)

    def config_false(self):
        return bool(self._node.flags & lib.LYS_CONFIG_R)

    def mandatory(self):
        return bool(self._node.flags & lib.LYS_MAND_TRUE)

    def deprecated(self):
        return bool(self._node.flags & lib.LYS_STATUS_DEPRC)

    def obsolete(self):
        return bool(self._node.flags & lib.LYS_STATUS_OBSLT)

    def status(self):
        if self._node.flags & lib.LYS_STATUS_DEPRC:
            return 'deprecated'
        elif self._node.flags & lib.LYS_STATUS_OBSLT:
            return 'obsolete'
        return 'current'

    def module(self):
        module_p = lib.lys_node_module(self._node)
        if not module_p:
            raise self.context.error('cannot get module')
        return Module(self.context, module_p)

    def schema_path(self):
        try:
            s = lib.lys_path(self._node, 0)
            return c2str(s)
        finally:
            lib.free(s)

    def data_path(self):
        try:
            s = lib.lypy_data_path_pattern(self._node)
            return c2str(s)
        finally:
            lib.free(s)

    def extensions(self):
        for i in range(self._node.ext_size):
            yield Extension(self.context, self._node.ext[i])

    def get_extension(self, name, prefix=None, arg_value=None):
        ext = lib.lypy_find_ext(
            self._node.ext, self._node.ext_size,
            str2c(name), str2c(prefix), str2c(arg_value))
        if ext:
            return Extension(self.context, ext)
        return None

    def if_features(self):
        for i in range(self._node.iffeature_size):
            yield IfFeatureExpr(self.context, self._node.iffeature[i])

    def parent(self):
        parent_p = lib.lys_parent(self._node)
        while parent_p and parent_p.nodetype not in SNode.NODETYPE_CLASS:
            parent_p = lib.lys_parent(parent_p)
        if parent_p:
            return SNode.new(self.context, parent_p)
        return None

    def __repr__(self):
        cls = self.__class__
        return '<%s.%s: %s>' % (cls.__module__, cls.__name__, str(self))

    def __str__(self):
        return self.name()

    NODETYPE_CLASS = {}

    @classmethod
    def register(cls, nodetype):
        def _decorator(nodeclass):
            cls.NODETYPE_CLASS[nodetype] = nodeclass
            return nodeclass
        return _decorator

    @classmethod
    def new(cls, context, node_p):
        nodecls = cls.NODETYPE_CLASS.get(node_p.nodetype, SNode)
        return nodecls(context, node_p)


#------------------------------------------------------------------------------
@SNode.register(SNode.LEAF)
class SLeaf(SNode):

    def __init__(self, context, node_p):
        SNode.__init__(self, context, node_p)
        self._leaf = ffi.cast('struct lys_node_leaf *', node_p)

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

    def must_conditions(self):
        for i in range(self._leaf.must_size):
            yield c2str(self._leaf.must[i].expr)

    def __str__(self):
        return '%s %s' % (self.name(), self.type().name())


#------------------------------------------------------------------------------
@SNode.register(SNode.LEAFLIST)
class SLeafList(SNode):

    def __init__(self, context, node_p):
        SNode.__init__(self, context, node_p)
        self._leaflist = ffi.cast('struct lys_node_leaflist *', node_p)

    def ordered(self):
        return bool(self._node.flags & lib.LYS_USERORDERED)

    def units(self):
        return c2str(self._leaflist.units)

    def type(self):
        return Type(self.context, ffi.addressof(self._leaflist.type))

    def defaults(self):
        for i in range(self._leaflist.dflt_size):
            yield c2str(self._leaflist.dflt[i])

    def must_conditions(self):
        for i in range(self._leaflist.must_size):
            yield c2str(self._leaflist.must[i].expr)

    def __str__(self):
        return '%s %s' % (self.name(), self.type().name())


#------------------------------------------------------------------------------
@SNode.register(SNode.CONTAINER)
class SContainer(SNode):

    def __init__(self, context, node_p):
        SNode.__init__(self, context, node_p)
        self._container = ffi.cast('struct lys_node_container *', node_p)

    def presence(self):
        return c2str(self._container.presence)

    def must_conditions(self):
        for i in range(self._container.must_size):
            yield c2str(self._container.must[i].expr)

    def __iter__(self):
        return self.children()

    def children(self, types=None):
        return iter_children(self.context, self._node, types=types)


#------------------------------------------------------------------------------
@SNode.register(SNode.LIST)
class SList(SNode):

    def __init__(self, context, node_p):
        SNode.__init__(self, context, node_p)
        self._list = ffi.cast('struct lys_node_list *', node_p)

    def ordered(self):
        return bool(self._node.flags & lib.LYS_USERORDERED)

    def __iter__(self):
        return self.children()

    def children(self, skip_keys=False, types=None):
        return iter_children(
            self.context, self._node, skip_keys=skip_keys, types=types)

    def keys(self):
        for i in range(self._list.keys_size):
            node = ffi.cast('struct lys_node *', self._list.keys[i])
            yield SLeaf(self.context, node)

    def must_conditions(self):
        for i in range(self._list.must_size):
            yield c2str(self._list.must[i].expr)

    def __str__(self):
        return '%s [%s]' % (
            self.name(), ', '.join(k.name() for k in self.keys()))


#------------------------------------------------------------------------------
@SNode.register(SNode.INPUT)
@SNode.register(SNode.OUTPUT)
class SRpcInOut(SNode):

    def __iter__(self):
        return self.children()

    def must_conditions(self):
        return ()

    def children(self, types=None):
        return iter_children(self.context, self._node, types=types)


#------------------------------------------------------------------------------
@SNode.register(SNode.RPC)
class SRpc(SNode):

    def must_conditions(self):
        return ()

    def input(self):
        try:
            return next(iter_children(
                self.context, self._node, types=(self.INPUT,),
                options=lib.LYS_GETNEXT_WITHINOUT))
        except StopIteration:
            return None

    def output(self):
        try:
            return next(iter_children(
                self.context, self._node, types=(self.OUTPUT,),
                options=lib.LYS_GETNEXT_WITHINOUT))
        except StopIteration:
            return None

    def __iter__(self):
        return self.children()

    def children(self, types=None):
        return iter_children(self.context, self._node, types=types)


#------------------------------------------------------------------------------
def iter_children(context, parent, skip_keys=False, types=None, options=0):
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

    if ffi.typeof(parent) == ffi.typeof('struct lys_module *'):
        module = parent
        parent = ffi.NULL
    else:
        module = ffi.NULL

    child = lib.lys_getnext(ffi.NULL, parent, module, options)
    while child:
        if not _skip(child):
            yield SNode.new(context, child)
        child = lib.lys_getnext(child, parent, module, options)


#------------------------------------------------------------------------------
# compat
Container = SContainer
Leaf = SLeaf
LeafList = SLeafList
List = SList
Node = SNode
Rpc = SRpc
RpcInOut = SRpcInOut
