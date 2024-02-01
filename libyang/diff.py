# Copyright (c) 2019 6WIND
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Iterator, Optional

from .context import Context
from .schema import SContainer, SLeaf, SLeafList, SList, SNode, SNotif, SRpc, SRpcInOut


# -------------------------------------------------------------------------------------
def schema_diff(
    ctx_old: Context,
    ctx_new: Context,
    exclude_node_cb: Optional[Callable[[SNode], bool]] = None,
    use_data_path: bool = False,
) -> Iterator["SNodeDiff"]:
    """
    Compare two libyang Context objects, for a given set of paths and return all
    differences.

    :arg ctx_old:
        The first context.
    :arg ctx_new:
        The second context.
    :arg exclude_node_cb:
        Optional user callback that will be called with each node that is found in each
        context. If the callback returns a "trueish" value, the node will be excluded
        from the diff (as well as all its children).
    :arg use_data_path:
        Use data path instead of schema path to compare the nodes. Using data path
        ignores choices and cases.

    :return:
        An iterator that yield `SNodeDiff` objects.
    """
    if exclude_node_cb is None:
        # pylint: disable=unnecessary-lambda-assignment
        exclude_node_cb = lambda n: False

    def flatten(node, dic):
        """
        Flatten a node and all its children into a dict (indexed by their schema xpath).
        This function is recursive.
        """
        if exclude_node_cb(node):
            return
        if use_data_path:
            path = node.data_path()
        else:
            path = node.schema_path()
        dic[path] = node
        if isinstance(node, (SContainer, SList, SNotif, SRpc, SRpcInOut)):
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
        yield from diffs[path]


# -------------------------------------------------------------------------------------
class SNodeDiff:
    __slots__ = ("__dict__",)


# -------------------------------------------------------------------------------------
class SNodeRemoved(SNodeDiff):
    __slots__ = ("node",)

    def __init__(self, node: SNode):
        self.node = node

    def __str__(self):
        return "-%s: removed status=%s %s" % (
            self.node.schema_path(),
            self.node.status(),
            self.node.keyword(),
        )


# -------------------------------------------------------------------------------------
class SNodeAdded(SNodeDiff):
    __slots__ = ("node",)

    def __init__(self, node: SNode):
        self.node = node

    def __str__(self):
        return "+%s: added %s" % (self.node.schema_path(), self.node.keyword())


# -------------------------------------------------------------------------------------
class SNodeAttributeChanged(SNodeDiff):
    __slots__ = ("old", "new", "value")

    def __init__(self, old: SNode, new: SNode, value: Any = None):
        self.old = old
        self.new = new
        self.value = value

    def __str__(self):
        if self.__class__.__name__.endswith("Added"):
            sign = "+"
        else:
            sign = "-"
        s = "%s%s: %s" % (sign, self.new.schema_path(), self.__class__.__name__)
        if self.value is not None:
            str_val = str(self.value).replace('"', '\\"').replace("\n", "\\n")
            s += ' "%s"' % str_val
        return s


# -------------------------------------------------------------------------------------
class BaseTypeRemoved(SNodeAttributeChanged):
    pass


class BaseTypeAdded(SNodeAttributeChanged):
    pass


class BitRemoved(SNodeAttributeChanged):
    pass


class BitAdded(SNodeAttributeChanged):
    pass


class BitStatusRemoved(SNodeAttributeChanged):
    pass


class BitStatusAdded(SNodeAttributeChanged):
    pass


class ConfigFalseRemoved(SNodeAttributeChanged):
    pass


class ConfigFalseAdded(SNodeAttributeChanged):
    pass


class DefaultRemoved(SNodeAttributeChanged):
    pass


class DefaultAdded(SNodeAttributeChanged):
    pass


class DescriptionRemoved(SNodeAttributeChanged):
    pass


class DescriptionAdded(SNodeAttributeChanged):
    pass


class EnumRemoved(SNodeAttributeChanged):
    pass


class EnumAdded(SNodeAttributeChanged):
    pass


class EnumStatusRemoved(SNodeAttributeChanged):
    pass


class EnumStatusAdded(SNodeAttributeChanged):
    pass


class ExtensionRemoved(SNodeAttributeChanged):
    pass


class ExtensionAdded(SNodeAttributeChanged):
    pass


class KeyRemoved(SNodeAttributeChanged):
    pass


class KeyAdded(SNodeAttributeChanged):
    pass


class MandatoryRemoved(SNodeAttributeChanged):
    pass


class MandatoryAdded(SNodeAttributeChanged):
    pass


class MustRemoved(SNodeAttributeChanged):
    pass


class MustAdded(SNodeAttributeChanged):
    pass


class NodeTypeAdded(SNodeAttributeChanged):
    pass


class NodeTypeRemoved(SNodeAttributeChanged):
    pass


class RangeRemoved(SNodeAttributeChanged):
    pass


class RangeAdded(SNodeAttributeChanged):
    pass


class OrderedByUserRemoved(SNodeAttributeChanged):
    pass


class OrderedByUserAdded(SNodeAttributeChanged):
    pass


class PresenceRemoved(SNodeAttributeChanged):
    pass


class PresenceAdded(SNodeAttributeChanged):
    pass


class StatusRemoved(SNodeAttributeChanged):
    pass


class StatusAdded(SNodeAttributeChanged):
    pass


class LengthRemoved(SNodeAttributeChanged):
    pass


class LengthAdded(SNodeAttributeChanged):
    pass


class PatternRemoved(SNodeAttributeChanged):
    pass


class PatternAdded(SNodeAttributeChanged):
    pass


class UnitsRemoved(SNodeAttributeChanged):
    pass


class UnitsAdded(SNodeAttributeChanged):
    pass


# -------------------------------------------------------------------------------------
def snode_changes(old: SNode, new: SNode) -> Iterator[SNodeDiff]:
    if old.nodetype() != new.nodetype():
        yield NodeTypeRemoved(old, new, old.keyword())
        yield NodeTypeAdded(old, new, new.keyword())

    if old.description() != new.description():
        if old.description() is not None:
            yield DescriptionRemoved(old, new, old.description())
        if new.description() is not None:
            yield DescriptionAdded(old, new, new.description())

    if old.mandatory() and not new.mandatory():
        yield MandatoryRemoved(old, new)
    elif not old.mandatory() and new.mandatory():
        yield MandatoryAdded(old, new)

    if old.status() != new.status():
        yield StatusRemoved(old, new, old.status())
        yield StatusAdded(old, new, new.status())

    if old.config_false() and not new.config_false():
        yield ConfigFalseRemoved(old, new)
    elif not old.config_false() and new.config_false():
        yield ConfigFalseAdded(old, new)

    old_musts = frozenset(old.must_conditions())
    new_musts = frozenset(new.must_conditions())
    for m in old_musts - new_musts:
        yield MustRemoved(old, new, m)
    for m in new_musts - old_musts:
        yield MustAdded(old, new, m)

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
            yield ExtensionRemoved(old, new, old_exts[k])
            yield ExtensionAdded(old, new, new_exts[k])

    if (isinstance(old, SLeaf) and isinstance(new, SLeaf)) or (
        isinstance(old, SLeafList) and isinstance(new, SLeafList)
    ):
        old_bases = set(old.type().basenames())
        new_bases = set(new.type().basenames())
        for b in old_bases - new_bases:
            yield BaseTypeRemoved(old, new, b)
        for b in new_bases - old_bases:
            yield BaseTypeAdded(old, new, b)

        if old.units() != new.units():
            if old.units() is not None:
                yield UnitsRemoved(old, new, old.units())
            if new.units() is not None:
                yield UnitsAdded(old, new, new.units())

        old_lengths = set(old.type().all_lengths())
        new_lengths = set(new.type().all_lengths())
        for l in old_lengths - new_lengths:
            yield LengthRemoved(old, new, l)
        for l in new_lengths - old_lengths:
            yield LengthAdded(old, new, l)

        # Multiple "pattern" statements on a single type are ANDed together (i.e. they
        # must all match). However, when a leaf type is an union of multiple string
        # typedefs with individual "pattern" statements, the patterns are ORed together
        # (i.e. one of them must match).
        #
        # This is not handled properly here as we flatten all patterns in a single set
        # and consider there is a difference if we remove/add one of them.
        #
        # The difference does not hold any information about which union branch it
        # relates to. This is way too complex.
        old_patterns = set(old.type().all_patterns())
        new_patterns = set(new.type().all_patterns())
        for p in old_patterns - new_patterns:
            yield PatternRemoved(old, new, p)
        for p in new_patterns - old_patterns:
            yield PatternAdded(old, new, p)

        old_ranges = set(old.type().all_ranges())
        new_ranges = set(new.type().all_ranges())
        for r in old_ranges - new_ranges:
            yield RangeRemoved(old, new, r)
        for r in new_ranges - old_ranges:
            yield RangeAdded(old, new, r)

        old_enums = {e.name(): e for e in old.type().all_enums()}
        new_enums = {e.name(): e for e in new.type().all_enums()}
        for e in old_enums.keys() - new_enums.keys():
            yield EnumRemoved(old, new, old_enums[e])
        for e in new_enums.keys() - old_enums.keys():
            yield EnumAdded(old, new, new_enums[e])
        for e in new_enums.keys() & old_enums.keys():
            o = old_enums[e]
            n = new_enums[e]
            if o.status() != n.status():
                yield EnumStatusRemoved(old, new, (o.name(), o.status()))
                yield EnumStatusAdded(old, new, (n.name(), n.status()))

        old_bits = {b.name(): b for b in old.type().all_bits()}
        new_bits = {b.name(): b for b in new.type().all_bits()}
        for b in old_bits.keys() - new_bits.keys():
            yield BitRemoved(old, new, old_bits[b])
        for b in new_bits.keys() - old_bits.keys():
            yield BitAdded(old, new, new_bits[b])
        for b in new_bits.keys() & old_bits.keys():
            o = old_bits[b]
            n = new_bits[b]
            if o.status() != n.status():
                yield BitStatusRemoved(old, new, (o.name(), o.status()))
                yield BitStatusAdded(old, new, (n.name(), n.status()))

    if isinstance(old, SLeaf) and isinstance(new, SLeaf):
        if old.default() != new.default():
            if old.default() is not None:
                yield DefaultRemoved(old, new, old.default())
            if new.default() is not None:
                yield DefaultAdded(old, new, new.default())

    elif isinstance(old, SLeafList) and isinstance(new, SLeafList):
        old_defaults = frozenset(old.defaults())
        new_defaults = frozenset(new.defaults())
        for d in old_defaults - new_defaults:
            yield DefaultRemoved(old, new, d)
        for d in new_defaults - old_defaults:
            yield DefaultAdded(old, new, d)
        if old.ordered() and not new.ordered():
            yield OrderedByUserRemoved(old, new)
        elif not old.ordered() and new.ordered():
            yield OrderedByUserAdded(old, new)

    elif isinstance(old, SContainer) and isinstance(new, SContainer):
        if old.presence() != new.presence():
            if old.presence() is not None:
                yield PresenceRemoved(old, new, old.presence())
            if new.presence() is not None:
                yield PresenceAdded(old, new, new.presence())

    elif isinstance(old, SList) and isinstance(new, SList):
        old_keys = frozenset(k.name() for k in old.keys())
        new_keys = frozenset(k.name() for k in new.keys())
        for k in old_keys - new_keys:
            yield KeyRemoved(old, new, k)
        for k in new_keys - old_keys:
            yield KeyAdded(old, new, k)
        if old.ordered() and not new.ordered():
            yield OrderedByUserRemoved(old, new)
        elif not old.ordered() and new.ordered():
            yield OrderedByUserAdded(old, new)
