# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import (
    Context,
    Extension,
    ExtensionParsed,
    IfFeature,
    IfOrFeatures,
    IOType,
    LibyangError,
    Module,
    Must,
    PAction,
    PActionInOut,
    PAnydata,
    Pattern,
    PAugment,
    PCase,
    PChoice,
    PContainer,
    PGrouping,
    PLeaf,
    PLeafList,
    PList,
    PNode,
    PNotif,
    PRefine,
    PType,
    PUses,
    Revision,
    SAnydata,
    SCase,
    SChoice,
    SContainer,
    SLeaf,
    SLeafList,
    SList,
    SNode,
    SRpc,
    Type,
)


YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


# -------------------------------------------------------------------------------------
class ModuleTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.module = self.ctx.load_module("yolo-system")

    def tearDown(self):
        self.module = None
        self.ctx.destroy()
        self.ctx = None

    def test_mod_print_mem(self):
        s = self.module.print("tree", IOType.MEMORY)
        self.assertGreater(len(s), 0)

        s = self.module.print_mem("tree")
        self.assertGreater(len(s), 0)

    def test_mod_attrs(self):
        self.assertEqual(self.module.name(), "yolo-system")
        self.assertEqual(self.module.description(), "YOLO.")
        self.assertEqual(self.module.prefix(), "sys")

    def test_mod_filepath(self):
        self.assertEqual(
            self.module.filepath(), os.path.join(YANG_DIR, "yolo/yolo-system.yang")
        )

    def test_mod_iter(self):
        children = list(iter(self.module))
        self.assertEqual(len(children), 6)

    def test_mod_children_rpcs(self):
        rpcs = list(self.module.children(types=(SNode.RPC,)))
        self.assertEqual(len(rpcs), 2)

    def test_mod_enable_features(self):
        self.assertFalse(self.module.feature_state("turbo-boost"))
        self.module.feature_enable("turbo-boost")
        self.module.feature_enable("*")
        self.assertTrue(self.module.feature_state("turbo-boost"))
        self.module.feature_disable_all()
        self.assertFalse(self.module.feature_state("turbo-boost"))
        self.module.feature_enable_all()
        self.assertTrue(self.module.feature_state("turbo-boost"))
        self.module.feature_disable_all()

    def test_mod_imports(self):
        imports = list(self.module.imports())
        self.assertEqual(imports[0].name(), "omg-extensions")
        self.assertEqual(imports[1].name(), "wtf-types")
        self.assertEqual(len(imports), 2)

    def test_mod_features(self):
        features = list(self.module.features())
        self.assertEqual(len(features), 2)

    def test_mod_get_feature(self):
        self.module.feature_enable("turbo-boost")
        feature = self.module.get_feature("turbo-boost")
        self.assertEqual(feature.name(), "turbo-boost")
        self.assertEqual(feature.description(), "Goes faster.")
        self.assertIsNone(feature.reference())
        self.assertTrue(feature.state())
        self.assertFalse(feature.deprecated())
        self.assertFalse(feature.obsolete())

    def test_mod_get_feature_not_found(self):
        with self.assertRaises(LibyangError):
            self.module.get_feature("does-not-exist")

    def test_mod_revisions(self):
        revisions = list(self.module.revisions())
        self.assertEqual(len(revisions), 2)
        self.assertIsInstance(revisions[0], Revision)
        self.assertEqual(revisions[0].date(), "1999-04-01")
        self.assertEqual(revisions[1].date(), "1990-04-01")


# -------------------------------------------------------------------------------------
class RevisionTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        mod = self.ctx.load_module("yolo-system")
        revisions = list(mod.revisions())
        self.revision = revisions[0]

    def tearDown(self):
        self.revision = None
        self.ctx.destroy()
        self.ctx = None

    def test_rev_date(self):
        self.assertEqual(self.revision.date(), "1999-04-01")

    def test_rev_reference(self):
        self.assertEqual(
            self.revision.reference(),
            "RFC 2549 - IP over Avian Carriers with Quality of Service.",
        )

    def test_rev_description(self):
        self.assertEqual(self.revision.description(), "Version update.")

    def test_rev_extensions(self):
        exts = list(self.revision.extensions())
        self.assertEqual(len(exts), 1)
        ext = self.revision.get_extension("human-name", prefix="omg-extensions")
        self.assertIsInstance(ext, Extension)


# -------------------------------------------------------------------------------------
class IfFeatureTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.mod = self.ctx.load_module("yolo-system")
        self.mod.feature_enable_all()
        self.leaf = next(
            self.ctx.find_path("/yolo-system:conf/yolo-system:isolation-level")
        )

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_iffeatures(self):
        iffeatures = list(self.leaf.if_features())
        self.assertEqual(len(iffeatures), 1)

    def test_iffeature_tree(self):
        iff = next(self.leaf.if_features())
        tree = iff.tree()
        self.assertIsInstance(tree, IfOrFeatures)
        self.assertIsInstance(tree.a, IfFeature)
        self.assertIsInstance(tree.b, IfFeature)
        self.assertEqual(tree.a.feature().name(), "turbo-boost")
        self.assertEqual(tree.b.feature().name(), "networking")

    def test_iffeature_state(self):
        def feature_disable_only(feature):
            self.mod.feature_disable_all()
            for f in self.mod.features():
                if f.name() == feature:
                    continue
                self.mod.feature_enable(f.name())

        leaf_simple = next(self.ctx.find_path("/yolo-system:conf/yolo-system:speed"))

        self.mod.feature_disable_all()
        leaf_not = next(self.ctx.find_path("/yolo-system:conf/yolo-system:offline"))
        self.mod.feature_enable_all()

        leaf_and = next(self.ctx.find_path("/yolo-system:conf/yolo-system:full"))
        leaf_or = next(
            self.ctx.find_path("/yolo-system:conf/yolo-system:isolation-level")
        )

        # if-feature is just a feature
        tree = next(leaf_simple.if_features()).tree()
        self.mod.feature_enable_all()
        self.assertEqual(tree.state(), True)
        self.mod.feature_disable_all()
        self.assertEqual(tree.state(), False)

        # if-feature is "NOT networking"
        tree = next(leaf_not.if_features()).tree()
        self.mod.feature_enable_all()
        self.assertEqual(tree.state(), False)
        self.mod.feature_disable_all()
        self.assertEqual(tree.state(), True)

        # if-feature is "turbo-boost AND networking"
        tree = next(leaf_and.if_features()).tree()
        self.mod.feature_enable_all()
        self.assertEqual(tree.state(), True)
        self.mod.feature_disable_all()
        self.assertEqual(tree.state(), False)
        feature_disable_only("turbo-boost")
        self.assertEqual(tree.state(), False)
        feature_disable_only("networking")
        self.assertEqual(tree.state(), False)

        # if-feature is "turbo-boost OR networking"
        tree = next(leaf_or.if_features()).tree()
        self.mod.feature_enable_all()
        self.assertEqual(tree.state(), True)
        self.mod.feature_disable_all()
        self.assertEqual(tree.state(), False)
        feature_disable_only("turbo-boost")
        self.assertEqual(tree.state(), True)
        feature_disable_only("networking")
        self.assertEqual(tree.state(), True)

    def test_iffeature_str(self):
        iff = next(self.leaf.if_features())
        self.assertEqual(str(iff), "turbo-boost OR networking")

    def test_iffeature_dump(self):
        iff = next(self.leaf.if_features())
        self.assertEqual(
            iff.dump(),
            """OR
 turbo-boost [Goes faster.]
 networking [Supports networking.]
""",
        )


# -------------------------------------------------------------------------------------
class ContainerTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        mod = self.ctx.load_module("yolo-system")
        mod.feature_enable_all()
        self.container = next(self.ctx.find_path("/yolo-system:conf"))

    def tearDown(self):
        self.container = None
        self.ctx.destroy()
        self.ctx = None

    def test_cont_attrs(self):
        self.assertIsInstance(self.container, SContainer)
        self.assertEqual(self.container.nodetype(), SNode.CONTAINER)
        self.assertEqual(self.container.keyword(), "container")
        self.assertEqual(self.container.name(), "conf")
        self.assertEqual(self.container.fullname(), "yolo-system:conf")
        self.assertEqual(self.container.description(), "Configuration.")
        self.assertEqual(self.container.config_set(), False)
        self.assertEqual(self.container.config_false(), False)
        self.assertEqual(self.container.mandatory(), False)
        self.assertIsInstance(self.container.module(), Module)
        self.assertEqual(self.container.schema_path(), "/yolo-system:conf")
        self.assertEqual(self.container.data_path(), "/yolo-system:conf")
        self.assertIs(self.container.presence(), None)

    def test_cont_iter(self):
        children = list(iter(self.container))
        self.assertEqual(len(children), 11)

    def test_cont_children_leafs(self):
        leafs = list(self.container.children(types=(SNode.LEAF,)))
        self.assertEqual(len(leafs), 9)
        without_choice = [c.name() for c in self.container.children(with_choice=False)]
        with_choice = [c.name() for c in self.container.children(with_choice=True)]
        self.assertTrue("pill" not in without_choice)
        self.assertTrue("pill" in with_choice)

    def test_cont_parent(self):
        self.assertIsNone(self.container.parent())

    def test_iter_tree(self):
        tree = list(self.container.iter_tree())
        self.assertEqual(len(tree), 20)
        tree = list(self.container.iter_tree(full=True))
        self.assertEqual(len(tree), 25)

    def test_container_parsed(self):
        pnode = self.container.parsed()
        self.assertIsInstance(pnode, PContainer)
        self.assertIsNone(next(pnode.musts(), None))
        self.assertIsNone(pnode.when_condition())
        self.assertIsNone(pnode.presence())
        self.assertIsNone(next(pnode.typedefs(), None))
        self.assertIsNone(next(pnode.groupings(), None))
        self.assertIsNotNone(next(iter(pnode)))
        self.assertIsNone(next(pnode.actions(), None))
        self.assertIsNone(next(pnode.notifications(), None))


# -------------------------------------------------------------------------------------
class UsesTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        mod = self.ctx.load_module("yolo-nodetypes")
        mod.feature_enable_all()

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_uses_parsed(self):
        snode = next(self.ctx.find_path("/yolo-nodetypes:cont2"))
        self.assertIsInstance(snode, SContainer)
        pnode = snode.parsed()
        self.assertIsInstance(pnode, PContainer)
        pnode = next(iter(pnode))
        self.assertIsInstance(pnode, PUses)

        ref_pnode = next(pnode.refines())
        self.assertIsInstance(ref_pnode, PRefine)
        self.assertEqual("cont3/leaf1", ref_pnode.nodeid())
        self.assertIsNone(ref_pnode.description())
        self.assertIsNone(ref_pnode.reference())
        self.assertIsNone(next(ref_pnode.if_features(), None))
        self.assertIsNone(next(ref_pnode.musts(), None))
        self.assertIsNone(ref_pnode.presence())
        self.assertIsNone(next(ref_pnode.defaults(), None))
        self.assertEqual(0, ref_pnode.min_elements())
        self.assertIsNone(ref_pnode.max_elements())
        self.assertIsNone(next(ref_pnode.extensions(), None))

        aug_pnode = next(pnode.augments())
        self.assertIsInstance(aug_pnode, PAugment)
        self.assertIsNotNone(next(iter(aug_pnode)))
        self.assertIsNone(aug_pnode.when_condition())
        self.assertIsNone(next(aug_pnode.actions(), None))
        self.assertIsNone(next(aug_pnode.notifications(), None))


# -------------------------------------------------------------------------------------
class GroupingTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_grouping_parsed(self):
        mod = self.ctx.load_module("yolo-nodetypes")
        pnode = next(mod.groupings())
        self.assertIsInstance(pnode, PGrouping)
        self.assertIsNone(next(pnode.typedefs(), None))
        self.assertIsNone(next(pnode.groupings(), None))
        child = next(iter(pnode))
        self.assertIsNotNone(child)
        self.assertIsNone(next(pnode.actions(), None))
        self.assertIsNone(next(pnode.notifications(), None))


# -------------------------------------------------------------------------------------
class ListTest(unittest.TestCase):
    PATH = {
        "LOG": "/yolo-system:conf/url",
        "DATA": "/yolo-system:conf/url",
        "DATA_PATTERN": "/yolo-system:conf/url[proto='%s'][host='%s']",
    }

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-system")
        self.ctx.load_module("yolo-nodetypes")
        self.list = next(self.ctx.find_path(self.PATH["LOG"]))

    def tearDown(self):
        self.list = None
        self.ctx.destroy()
        self.ctx = None

    def test_list_attrs(self):
        self.assertIsInstance(self.list, SList)
        self.assertEqual(self.list.nodetype(), SNode.LIST)
        self.assertEqual(self.list.keyword(), "list")

        self.assertEqual(self.list.schema_path(), self.PATH["LOG"])

        self.assertEqual(self.list.schema_path(SNode.PATH_DATA), self.PATH["DATA"])

        self.assertEqual(self.list.data_path(), self.PATH["DATA_PATTERN"])
        self.assertFalse(self.list.ordered())

    def test_list_keys(self):
        keys = list(self.list.keys())
        self.assertEqual(len(keys), 2)

    def test_list_iter(self):
        children = list(iter(self.list))
        self.assertEqual(len(children), 6)

    def test_list_children_skip_keys(self):
        children = list(self.list.children(skip_keys=True))
        self.assertEqual(len(children), 4)

    def test_list_parent(self):
        parent = self.list.parent()
        self.assertIsNotNone(parent)
        self.assertIsInstance(parent, SContainer)
        self.assertEqual(parent.name(), "conf")

    def test_list_uniques(self):
        list1 = next(self.ctx.find_path("/yolo-nodetypes:conf/list1"))
        self.assertIsInstance(list1, SList)
        uniques = list(list1.uniques())
        self.assertEqual(len(uniques), 1)
        elements = [u.name() for u in uniques[0]]
        self.assertEqual(len(elements), 2)
        self.assertTrue("leaf2" in elements)
        self.assertTrue("leaf3" in elements)

        list2 = next(self.ctx.find_path("/yolo-nodetypes:conf/list2"))
        self.assertIsInstance(list2, SList)
        uniques = list(list2.uniques())
        self.assertEqual(len(uniques), 0)

    def test_list_min_max(self):
        list1 = next(self.ctx.find_path("/yolo-nodetypes:conf/list1"))
        self.assertIsInstance(list1, SList)
        self.assertEqual(list1.min_elements(), 2)
        self.assertEqual(list1.max_elements(), 10)

        list2 = next(self.ctx.find_path("/yolo-nodetypes:conf/list2"))
        self.assertIsInstance(list2, SList)
        self.assertEqual(list2.min_elements(), 0)
        self.assertEqual(list2.max_elements(), None)

    def test_list_parsed(self):
        list1 = next(self.ctx.find_path("/yolo-nodetypes:conf/list1"))
        self.assertIsInstance(list1, SList)
        pnode = list1.parsed()
        self.assertIsInstance(pnode, PList)
        self.assertIsNone(next(pnode.musts(), None))
        self.assertIsNone(pnode.when_condition())
        self.assertEqual("leaf1", pnode.key())
        self.assertIsNone(next(pnode.typedefs(), None))
        self.assertIsNone(next(pnode.groupings(), None))
        child = next(iter(pnode))
        self.assertIsInstance(child, PLeaf)
        self.assertIsNone(next(pnode.actions(), None))
        self.assertIsNone(next(pnode.notifications(), None))
        self.assertEqual("leaf2 leaf3", next(pnode.uniques()))
        self.assertEqual(2, pnode.min_elements())
        self.assertEqual(10, pnode.max_elements())
        self.assertFalse(pnode.ordered())


# -------------------------------------------------------------------------------------
class RpcTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-system")
        self.rpc = next(self.ctx.find_path("/yolo-system:format-disk"))

    def tearDown(self):
        self.rpc = None
        self.ctx.destroy()
        self.ctx = None

    def test_rpc_attrs(self):
        self.assertIsInstance(self.rpc, SRpc)
        self.assertEqual(self.rpc.nodetype(), SNode.RPC)
        self.assertEqual(self.rpc.keyword(), "rpc")
        self.assertEqual(self.rpc.schema_path(), "/yolo-system:format-disk")

    def test_rpc_extensions(self):
        ext = list(self.rpc.extensions())
        self.assertEqual(len(ext), 1)
        ext = self.rpc.get_extension("require-admin", prefix="omg-extensions")
        self.assertIsInstance(ext, Extension)
        self.assertIsInstance(ext.parent_node(), SRpc)
        parsed = self.rpc.parsed()
        ext = parsed.get_extension("require-admin", prefix="omg-extensions")
        self.assertIsInstance(ext, ExtensionParsed)
        self.assertIsInstance(ext.parent_node(), PAction)

    def test_rpc_params(self):
        leaf = next(self.rpc.children())
        self.assertIsInstance(leaf, SLeaf)
        self.assertEqual(leaf.data_path(), "/yolo-system:format-disk/disk")
        leaf = next(self.rpc.input().children())
        self.assertIsInstance(leaf, SLeaf)

    def test_rpc_no_parent(self):
        self.assertIsNone(self.rpc.parent())

    def test_rpc_parsed(self):
        self.assertIsInstance(self.rpc, SRpc)
        pnode = self.rpc.parsed()
        self.assertIsInstance(pnode, PAction)
        self.assertIsNone(next(pnode.typedefs(), None))
        self.assertIsNone(next(pnode.groupings(), None))
        pnode2 = pnode.input()
        self.assertIsInstance(pnode2, PActionInOut)
        self.assertIsInstance(pnode.output(), PActionInOut)
        self.assertIsNone(next(pnode2.musts(), None))
        self.assertIsNone(next(pnode2.typedefs(), None))
        self.assertIsNone(next(pnode2.groupings(), None))
        pnode3 = next(iter(pnode2))
        self.assertIsInstance(pnode3, PLeaf)


# -------------------------------------------------------------------------------------
class LeafTypeTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-system")

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_leaf_type_derived(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:hostname"))
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), "types:host")
        self.assertEqual(t.base(), Type.STRING)
        mod = t.module()
        self.assertIsNot(mod, None)
        self.assertEqual(mod.name(), "yolo-system")
        self.assertEqual(mod.get_module_from_prefix("types").name(), "wtf-types")
        self.assertEqual(t.typedef().name(), "host")
        self.assertEqual(t.typedef().description(), "my host type.")
        self.assertEqual(t.description(), "my host type.")

    def test_leaf_type_status(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:hostname"))
        self.assertIsInstance(leaf, SLeaf)
        self.assertEqual(leaf.deprecated(), False)
        self.assertEqual(leaf.obsolete(), False)
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:deprecated-leaf"))
        self.assertIsInstance(leaf, SLeaf)
        self.assertEqual(leaf.deprecated(), True)
        self.assertEqual(leaf.obsolete(), False)
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:obsolete-leaf"))
        self.assertIsInstance(leaf, SLeaf)
        self.assertEqual(leaf.deprecated(), False)
        self.assertEqual(leaf.obsolete(), True)

    def test_leaf_type_pattern(self):
        leaf = next(
            self.ctx.find_path("/yolo-system:conf/yolo-system:url/yolo-system:host")
        )
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(list(t.patterns()), [("[a-z.]+", False), ("1", True)])
        patterns = list(t.all_pattern_details())
        self.assertEqual(len(patterns), 2)
        self.assertIsInstance(patterns[0], Pattern)
        self.assertEqual(patterns[0].expression(), "[a-z.]+")
        self.assertFalse(patterns[0].inverted())
        self.assertEqual(patterns[0].error_message(), "ERROR1")
        self.assertEqual(patterns[1].expression(), "1")
        self.assertTrue(patterns[1].inverted())
        self.assertIsNone(patterns[1].error_message())

    def test_leaf_type_union(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:number"))
        self.assertIsInstance(leaf, SLeafList)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), "types:number")
        self.assertEqual(t.base(), Type.UNION)
        types = set(u.name() for u in t.union_types())
        types2 = set(u.name() for u in t.union_types(with_typedefs=True))
        self.assertEqual(types, set(["int16", "int32", "uint16", "uint32"]))
        self.assertEqual(types2, set(["signed", "unsigned"]))
        for u in t.union_types():
            ext = u.get_extension(
                "type-desc", prefix="omg-extensions", arg_value=f"<{u.name()}>"
            )
            self.assertIsInstance(ext, Extension)
            self.assertEqual(len(list(u.extensions())), 2)
        bases = set(t.basenames())
        self.assertEqual(bases, set(["int16", "int32", "uint16", "uint32"]))

    def test_leaf_type_extensions(self):
        leaf = next(
            self.ctx.find_path("/yolo-system:conf/yolo-system:url/yolo-system:proto")
        )
        t = leaf.type()
        ext = t.get_extension(
            "type-desc", prefix="omg-extensions", arg_value="<protocol>"
        )
        self.assertIsInstance(ext, Extension)
        self.assertIsNone(ext.parent_node())

    def test_leaf_type_enum(self):
        leaf = next(
            self.ctx.find_path("/yolo-system:conf/yolo-system:url/yolo-system:proto")
        )
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), "types:protocol")
        self.assertEqual(t.base(), Type.ENUM)
        enums = [e.name() for e in t.enums()]
        self.assertEqual(enums, ["http", "https", "ftp", "sftp"])

    def test_leaf_type_bits(self):
        leaf = next(self.ctx.find_path("/yolo-system:chmod/yolo-system:perms"))
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), "types:permissions")
        self.assertEqual(t.base(), Type.BITS)
        bits = [b.name() for b in t.bits()]
        self.assertEqual(bits, ["read", "write", "execute"])

    def test_leaf_parent(self):
        leaf = next(
            self.ctx.find_path("/yolo-system:conf/yolo-system:url/yolo-system:proto")
        )
        parent = leaf.parent()
        self.assertIsNotNone(parent)
        self.assertIsInstance(parent, SList)
        self.assertEqual(parent.name(), "url")

    def test_iter_tree(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf"))
        self.assertEqual(len(list(leaf.iter_tree(full=True))), 23)

    def test_leaf_type_fraction_digits(self):
        self.ctx.load_module("yolo-nodetypes")
        leaf = next(self.ctx.find_path("/yolo-nodetypes:conf/percentage"))
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(next(t.all_fraction_digits(), None), 2)

    def test_leaf_type_require_instance(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf/hostname-ref"))
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertFalse(t.require_instance())

    def test_leaf_type_parsed(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:hostname"))
        self.assertIsInstance(leaf, SLeaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        pnode = t.parsed()
        self.assertIsInstance(pnode, PType)
        self.assertEqual("types:host", pnode.name())
        self.assertIsNone(pnode.range())
        self.assertIsNone(pnode.length())
        self.assertIsNone(next(pnode.patterns(), None))
        self.assertIsNone(next(pnode.enums(), None))
        self.assertIsNone(next(pnode.bits(), None))
        self.assertIsNone(pnode.path())
        self.assertIsNone(next(pnode.bases(), None))
        self.assertIsNone(next(pnode.types(), None))
        self.assertIsNone(next(pnode.extensions(), None))
        self.assertIsNotNone(pnode.pmod())
        self.assertIsNone(pnode.compiled())
        self.assertEqual(0, pnode.fraction_digits())
        self.assertFalse(pnode.require_instance())


# -------------------------------------------------------------------------------------
class LeafTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-nodetypes")

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_must(self):
        leaf = next(self.ctx.find_path("/yolo-nodetypes:conf/percentage"))
        self.assertIsInstance(leaf, SLeaf)
        must = next(leaf.musts(), None)
        self.assertIsInstance(must, Must)
        self.assertEqual(must.error_message(), "ERROR1")
        must = next(leaf.must_conditions(), None)
        self.assertIsInstance(must, str)

    def test_leaf_default(self):
        leaf = next(self.ctx.find_path("/yolo-nodetypes:conf/percentage"))
        self.assertIsInstance(leaf.default(), float)

    def test_leaf_parsed(self):
        leaf = next(self.ctx.find_path("/yolo-nodetypes:conf/percentage"))
        self.assertIsInstance(leaf, SLeaf)
        pnode = leaf.parsed()
        self.assertIsInstance(pnode, PLeaf)
        must = next(pnode.musts())
        self.assertIsInstance(must, Must)
        self.assertEqual(must.error_message(), "ERROR1")
        must = next(leaf.must_conditions())
        self.assertIsInstance(must, str)
        self.assertIsNone(pnode.when_condition())
        self.assertIsInstance(pnode.type(), PType)
        self.assertIsNone(pnode.units())
        self.assertEqual("10.2", pnode.default())
        self.assertFalse(pnode.is_key())

        # test basic PNode settings
        self.assertIsNotNone(pnode.parent())
        self.assertEqual(PNode.LEAF, pnode.nodetype())
        self.assertIsNotNone(next(pnode.siblings()))
        self.assertEqual("<libyang.schema.PLeaf: percentage>", repr(pnode))
        self.assertIsNone(pnode.description())
        self.assertIsNone(pnode.reference())
        self.assertIsNone(next(pnode.if_features(), None))
        self.assertIsNone(next(pnode.extensions(), None))
        self.assertIsNone(pnode.get_extension("test", prefix="test"))
        self.assertFalse(pnode.config_set())
        self.assertFalse(pnode.config_false())
        self.assertFalse(pnode.mandatory())
        self.assertFalse(pnode.deprecated())
        self.assertFalse(pnode.obsolete())
        self.assertEqual("current", pnode.status())

    NODETYPE_CLASS = {}


# -------------------------------------------------------------------------------------
class LeafListTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-nodetypes")

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_leaflist_defaults(self):
        leaflist = next(self.ctx.find_path("/yolo-nodetypes:conf/ratios"))
        for d in leaflist.defaults():
            self.assertIsInstance(d, float)
        leaflist = next(self.ctx.find_path("/yolo-nodetypes:conf/bools"))
        for d in leaflist.defaults():
            self.assertIsInstance(d, bool)
        leaflist = next(self.ctx.find_path("/yolo-nodetypes:conf/integers"))
        for d in leaflist.defaults():
            self.assertIsInstance(d, int)

    def test_leaf_list_min_max(self):
        leaflist1 = next(self.ctx.find_path("/yolo-nodetypes:conf/leaf-list1"))
        self.assertIsInstance(leaflist1, SLeafList)
        self.assertEqual(leaflist1.min_elements(), 3)
        self.assertEqual(leaflist1.max_elements(), 11)

        leaflist2 = next(self.ctx.find_path("/yolo-nodetypes:conf/leaf-list2"))
        self.assertIsInstance(leaflist2, SLeafList)
        self.assertEqual(leaflist2.min_elements(), 0)
        self.assertEqual(leaflist2.max_elements(), None)

    def test_leaf_list_parsed(self):
        leaflist = next(self.ctx.find_path("/yolo-nodetypes:conf/ratios"))
        self.assertIsInstance(leaflist, SLeafList)
        pnode = leaflist.parsed()
        self.assertIsInstance(pnode, PLeafList)
        self.assertIsNone(next(pnode.musts(), None))
        self.assertIsNone(pnode.when_condition())
        self.assertIsInstance(pnode.type(), PType)
        self.assertIsNone(pnode.units())
        self.assertEqual("2.5", next(pnode.defaults()))
        self.assertEqual(0, pnode.min_elements())
        self.assertIsNone(pnode.max_elements())
        self.assertFalse(pnode.ordered())


# -------------------------------------------------------------------------------------
class ChoiceTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-system")

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_choice_default(self):
        conf = next(self.ctx.find_path("/yolo-system:conf"))
        choice = next(conf.children((SNode.CHOICE,), with_choice=True))
        self.assertIsInstance(choice, SChoice)
        self.assertIsInstance(choice.default(), SCase)

    def test_choice_parsed(self):
        conf = next(self.ctx.find_path("/yolo-system:conf"))
        choice = next(conf.children((SNode.CHOICE,), with_choice=True))
        self.assertIsInstance(choice, SChoice)
        pnode = choice.parsed()
        self.assertIsInstance(pnode, PChoice)

        case_pnode = next(iter(pnode))
        self.assertIsInstance(case_pnode, PCase)
        self.assertIsNotNone(next(iter(case_pnode)))
        self.assertIsNone(case_pnode.when_condition())

        self.assertIsNone(pnode.when_condition())
        self.assertEqual("red", pnode.default())


# -------------------------------------------------------------------------------------
class AnydataTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-nodetypes")

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_anydata_parsed(self):
        snode = next(self.ctx.find_path("/yolo-nodetypes:any1"))
        self.assertIsInstance(snode, SAnydata)
        pnode = snode.parsed()
        self.assertIsInstance(pnode, PAnydata)
        self.assertIsNone(next(pnode.musts(), None))
        self.assertEqual("../cont2", pnode.when_condition())


# -------------------------------------------------------------------------------------
class NotificationTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-nodetypes")

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_notification_parsed(self):
        snode = next(self.ctx.find_path("/yolo-nodetypes:cont2"))
        self.assertIsInstance(snode, SContainer)
        pnode = snode.parsed()
        self.assertIsInstance(pnode, PContainer)
        pnode = next(pnode.notifications())
        self.assertIsInstance(pnode, PNotif)
        self.assertIsNone(next(pnode.musts(), None))
        self.assertIsNone(next(pnode.typedefs(), None))
        self.assertIsNone(next(pnode.groupings(), None))
        self.assertIsNotNone(next(iter(pnode)))
