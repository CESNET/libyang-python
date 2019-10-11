# Copyright (c) 2019 6WIND
# SPDX-License-Identifier: MIT

from . import schema


#------------------------------------------------------------------------------
def schema_diff(ctx_old, ctx_new, exclude_node_cb=None):
    """
    Compare two libyang :cls:`.Context`\s, for a given set of paths and return
    all differences.

    :arg Context ctx_old:
        The first context.
    :arg Context ctx_new:
        The second context.
    :arg <func> exclude_node_cb:
        Optionnal user callback that will be called with each node that is
        found in each context. If the callback returns a "trueish" value, the
        node will be excluded from the diff (as well as all its children).

    :return:
        An iterator that yield :cls:`.SNodeDiff` objects.
    """
    if exclude_node_cb is None:
        exclude_node_cb = lambda n: False

    def flatten(node, dic):
        """
        Flatten a node and all its children into a dict (indexed by their
        schema xpath). This function is recursive.
        """
        if exclude_node_cb(node):
            return
        dic[node.schema_path()] = node
        if isinstance(node, (schema.Container, schema.List, schema.Rpc, schema.RpcInOut)):
            for child in node:
                flatten(child, dic)

    old_dict = {}
    new_dict = {}

    for module in ctx_old:
        for node in module:
            flatten(node, old_dict)
    for module in ctx_new:
        for node in module:
            flatten(node, new_dict)

    diffs = {}
    old_paths = frozenset(old_dict.keys())
    new_paths = frozenset(new_dict.keys())
    for path in old_paths - new_paths:
        diffs[path] = [SNodeRemoved(old_dict[path])]
    for path in new_paths - old_paths:
        diffs[path] = [SNodeAdded(new_dict[path])]
    for path in old_paths & new_paths:
        old = old_dict[path]
        new = new_dict[path]
        diffs[path] = snode_changes(old, new)

    for path in sorted(diffs.keys()):
        for d in diffs[path]:
            yield d


#------------------------------------------------------------------------------
class SNodeDiff:
    pass


#------------------------------------------------------------------------------
class SNodeRemoved(SNodeDiff):

    def __init__(self, node):
        self.node = node

    def __str__(self):
        return '-%s: removed status=%s node' % (
            self.node.schema_path(), self.node.status())


#------------------------------------------------------------------------------
class SNodeAdded(SNodeDiff):

    def __init__(self, node):
        self.node = node

    def __str__(self):
        return '+%s: added node' % self.node.schema_path()


#------------------------------------------------------------------------------
def snode_changes(old, new):

    if old.nodetype() != new.nodetype():
        yield NodetypeChanged(old, new)

    if old.description() != new.description():
        yield DescriptionChanged(old, new)

    if old.mandatory() != new.mandatory():
        yield MandatoryChanged(old, new)

    if old.status() != new.status():
        yield StatusChanged(old, new)

    if old.config_false() != new.config_false():
        yield ConfigFalseChanged(old, new)

    old_musts = set(old.must_conditions())
    new_musts = set(new.must_conditions())
    for m in old_musts - new_musts:
        yield MustConditionRemoved(old, new, m)
    for m in new_musts - old_musts:
        yield MustConditionAdded(old, new, m)

    old_exts = {(e.module().name(), e.name()): e for e in old.extensions()}
    new_exts = {(e.module().name(), e.name()): e for e in new.extensions()}
    old_ext_keys = frozenset(old_exts.keys())
    new_ext_keys = frozenset(new_exts.keys())

    for k in old_ext_keys - new_ext_keys:
        yield ExtensionRemoved(old, new, old_exts[k])
    for k in new_ext_keys - old_ext_keys:
        yield ExtensionAdded(old, new, new_exts[k])
    for k in old_ext_keys & new_ext_keys:
        if old_exts[k].argument() != new_exts[k].argument():
            yield ExtensionChanged(old, new, old_exts[k], new_exts[k])

    if (isinstance(old, schema.Leaf) and isinstance(new, schema.Leaf)) or \
            (isinstance(old, schema.LeafList) and isinstance(new, schema.LeafList)):

        old_bases = set(old.type().basenames())
        new_bases = set(new.type().basenames())
        for b in old_bases - new_bases:
            yield BaseTypeRemoved(old, new, b)
        for b in new_bases - old_bases:
            yield BaseTypeAdded(old, new, b)

        if old.units() != new.units():
            yield UnitsChanged(old, new)

        old_lengths = set(old.type().all_lengths())
        new_lengths = set(new.type().all_lengths())
        for l in old_lengths - new_lengths:
            yield StringLengthRestrictionRemoved(old, new, l)
        for l in new_lengths - old_lengths:
            yield StringLengthRestrictionAdded(old, new, l)

        # Multiple "pattern" statements on a single type are ANDed together
        # (i.e. they must all match). However, when a leaf type is an union of
        # multiple string typedefs with individual "pattern" statements, the
        # patterns are ORed together (i.e. one of them must match).
        #
        # This is not handled properly here as we flatten all patterns in a
        # single set and consider there is a difference if we remove/add one of
        # them.
        #
        # The difference does not hold any information about which union branch
        # it relates to. This is way too complex.
        old_patterns = set(old.type().all_patterns())
        new_patterns = set(new.type().all_patterns())
        for p in old_patterns - new_patterns:
            yield StringPatternRestrictionRemoved(old, new, p)
        for p in new_patterns - old_patterns:
            yield StringPatternRestrictionAdded(old, new, p)

        old_ranges = set(old.type().all_ranges())
        new_ranges = set(new.type().all_ranges())
        for r in old_ranges - new_ranges:
            yield NumRangeRestrictionRemoved(old, new, r)
        for r in new_ranges - old_ranges:
            yield NumRangeRestrictionAdded(old, new, r)

        old_enums = set(e for e, _ in old.type().all_enums())
        new_enums = set(e for e, _ in new.type().all_enums())
        for e in old_enums - new_enums:
            yield EnumRemoved(old, new, e)
        for e in new_enums - old_enums:
            yield EnumAdded(old, new, e)

        old_bits = set(b for b, _ in old.type().all_bits())
        new_bits = set(b for b, _ in new.type().all_bits())
        for b in old_bits - new_bits:
            yield BitRemoved(old, new, b)
        for b in new_bits - old_bits:
            yield BitAdded(old, new, b)

    if isinstance(old, schema.Leaf) and isinstance(new, schema.Leaf):
        if old.default() != new.default():
            yield DefaultChanged(old, new)

    elif isinstance(old, schema.LeafList) and isinstance(new, schema.LeafList):
        if tuple(old.defaults()) != tuple(new.defaults()):
            yield DefaultsChanged(old, new)
        if old.ordered() != new.ordered():
            yield OrderedChanged(old, new)

    elif isinstance(old, schema.Container) and isinstance(new, schema.Container):
        if old.presence() != new.presence():
            yield PresenceChanged(old, new)

    elif isinstance(old, schema.List) and isinstance(new, schema.List):
        if {k.name() for k in old.keys()} != {k.name() for k in new.keys()}:
            yield KeyChanged(old, new)
        if old.ordered() != new.ordered():
            yield OrderedChanged(old, new)


#------------------------------------------------------------------------------
class SNodeChange(SNodeDiff):

    def __init__(self, old, new):
        self.old = old
        self.new = new

    def attribute_name(self):
        raise NotImplementedError()

    def attribute_value(self, node):
        raise NotImplementedError()

    def __str__(self):
        return '*{path}: {name} "{old_value}" -> "{new_value}"'.format(
            path=self.new.schema_path(),
            name=self.attribute_name(),
            old_value=self.attribute_value(self.old) or '',
            new_value=self.attribute_value(self.new) or '')


#------------------------------------------------------------------------------
class NodetypeChanged(SNodeChange):

    def attribute_name(self):
        return 'node-type'

    def attribute_value(self, node):
        return node.keyword()


#------------------------------------------------------------------------------
class DescriptionChanged(SNodeChange):

    def attribute_name(self):
        return 'description'

    def attribute_value(self, node):
        return node.description()


#------------------------------------------------------------------------------
class MandatoryChanged(SNodeChange):

    def attribute_name(self):
        return 'mandatory'

    def attribute_value(self, node):
        return 'true' if node.mandatory() else 'false'


#------------------------------------------------------------------------------
class StatusChanged(SNodeChange):

    def attribute_name(self):
        return 'status'

    def attribute_value(self, node):
        return node.status()


#------------------------------------------------------------------------------
class ConfigFalseChanged(SNodeChange):

    def attribute_name(self):
        return 'config'

    def attribute_value(self, node):
        if node.config_false():
            return 'false'
        return None


#------------------------------------------------------------------------------
class ExtensionRemoved(SNodeDiff):

    def __init__(self, old, new, ext):
        self.old = old
        self.new = new
        self.ext = ext

    def __str__(self):
        return '-{path}: extension {module}:{name} "{argument}"'.format(
            path=self.new.schema_path(),
            module=self.ext.module().name(),
            name=self.ext.name(),
            argument=self.ext.argument())


#------------------------------------------------------------------------------
class ExtensionAdded(SNodeDiff):

    def __init__(self, old, new, ext):
        self.old = old
        self.new = new
        self.ext = ext

    def __str__(self):
        return '+{path}: extension {module}:{name} "{argument}"'.format(
            path=self.new.schema_path(),
            module=self.ext.module().name(),
            name=self.ext.name(),
            argument=self.ext.argument())


#------------------------------------------------------------------------------
class ExtensionChanged(SNodeDiff):

    def __init__(self, old, new, old_ext, new_ext):
        self.old = old
        self.new = new
        self.old_ext = old_ext
        self.new_ext = new_ext

    def __str__(self):
        return '*{path}: extension {module}:{name} "{old}" -> "{new}"'.format(
            path=self.new.schema_path(),
            module=self.new_ext.module().name(),
            name=self.new_ext.name(),
            old=self.old_ext.argument() or '',
            new=self.new_ext.argument() or '')


#------------------------------------------------------------------------------
class DefaultChanged(SNodeChange):

    def attribute_name(self):
        return 'default'

    def attribute_value(self, node):
        return node.default()


#------------------------------------------------------------------------------
class UnitsChanged(SNodeChange):

    def attribute_name(self):
        return 'units'

    def attribute_value(self, node):
        return node.units()


#------------------------------------------------------------------------------
class KeyChanged(SNodeChange):

    def attribute_name(self):
        return 'key'

    def attribute_value(self, node):
        return ' '.join(sorted(k.name() for k in node.keys()))


#------------------------------------------------------------------------------
class DefaultsChanged(SNodeChange):

    def attribute_name(self):
        return 'defaults'

    def attribute_value(self, node):
        return ', '.join(node.defaults())


#------------------------------------------------------------------------------
class OrderedChanged(SNodeChange):

    def attribute_name(self):
        return 'ordered'

    def attribute_value(self, node):
        return 'true' if node.ordered() else 'false'


#------------------------------------------------------------------------------
class PresenceChanged(SNodeChange):

    def attribute_name(self):
        return 'presence'

    def attribute_value(self, node):
        return node.presence()


#------------------------------------------------------------------------------
class SNodeOptionChanged(SNodeDiff):

    def __init__(self, old, new, value):
        self.old = old
        self.new = new
        self.value = value

    def sign(self):
        raise NotImplementedError()

    def option_name(self):
        raise NotImplementedError()

    def __str__(self):
        return '{sign}{path}: {name} "{value}"'.format(
            sign=self.sign(),
            path=self.new.schema_path(),
            name=self.option_name(),
            value=self.value)


#------------------------------------------------------------------------------
class MustConditionRemoved(SNodeOptionChanged):

    def sign(self):
        return '-'

    def option_name(self):
        return 'must'


#------------------------------------------------------------------------------
class MustConditionAdded(SNodeOptionChanged):

    def sign(self):
        return '+'

    def option_name(self):
        return 'must'


#------------------------------------------------------------------------------
class BaseTypeRemoved(SNodeOptionChanged):

    def sign(self):
        return '-'

    def option_name(self):
        return 'base-type'


#------------------------------------------------------------------------------
class BaseTypeAdded(SNodeOptionChanged):

    def sign(self):
        return '+'

    def option_name(self):
        return 'base-type'


#------------------------------------------------------------------------------
class StringLengthRestrictionRemoved(SNodeOptionChanged):

    def sign(self):
        return '-'

    def option_name(self):
        return 'length'


#------------------------------------------------------------------------------
class StringLengthRestrictionAdded(SNodeOptionChanged):

    def sign(self):
        return '+'

    def option_name(self):
        return 'length'


#------------------------------------------------------------------------------
class NumRangeRestrictionRemoved(SNodeOptionChanged):

    def sign(self):
        return '-'

    def option_name(self):
        return 'range'


#------------------------------------------------------------------------------
class NumRangeRestrictionAdded(SNodeOptionChanged):

    def sign(self):
        return '+'

    def option_name(self):
        return 'range'


#------------------------------------------------------------------------------
class EnumRemoved(SNodeOptionChanged):

    def sign(self):
        return '-'

    def option_name(self):
        return 'enum'


#------------------------------------------------------------------------------
class EnumAdded(SNodeOptionChanged):

    def sign(self):
        return '+'

    def option_name(self):
        return 'enum'


#------------------------------------------------------------------------------
class BitRemoved(SNodeOptionChanged):

    def sign(self):
        return '-'

    def option_name(self):
        return 'bit'


#------------------------------------------------------------------------------
class BitAdded(SNodeOptionChanged):

    def sign(self):
        return '+'

    def option_name(self):
        return 'bit'


#------------------------------------------------------------------------------
class StringPatternRestrictionRemoved(SNodeDiff):

    def __init__(self, old, new, value):
        self.old = old
        self.new = new
        self.pattern, self.invert_match = value

    def __str__(self):
        return '-{path}: pattern "{pattern}"{invert_match}'.format(
            path=self.new.schema_path(),
            pattern=self.pattern,
            invert_match=' invert-match' if self.invert_match else '')


#------------------------------------------------------------------------------
class StringPatternRestrictionAdded(SNodeOptionChanged):

    def __init__(self, old, new, value):
        self.old = old
        self.new = new
        self.pattern, self.invert_match = value

    def __str__(self):
        return '+{path}: pattern "{pattern}"{invert_match}'.format(
            path=self.new.schema_path(),
            pattern=self.pattern,
            invert_match=' invert-match' if self.invert_match else '')
