# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import (
    Context,
    Extension,
    IfFeature,
    IfOrFeatures,
    IOType,
    LibyangError,
    Module,
    Revision,
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
        self.assertEqual(len(children), 5)

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
        self.assertEqual(len(children), 9)

    def test_cont_children_leafs(self):
        leafs = list(self.container.children(types=(SNode.LEAF,)))
        self.assertEqual(len(leafs), 7)

    def test_cont_parent(self):
        self.assertIsNone(self.container.parent())

    def test_iter_tree(self):
        tree = list(self.container.iter_tree())
        self.assertEqual(len(tree), 15)
        tree = list(self.container.iter_tree(full=True))
        self.assertEqual(len(tree), 20)


# -------------------------------------------------------------------------------------
class ListTest(unittest.TestCase):
    SCHEMA_PATH = "/yolo-system:conf/url"
    DATA_PATH = "/yolo-system:conf/url[host='%s'][proto='%s']"

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module("yolo-system")
        self.list = next(self.ctx.find_path(self.SCHEMA_PATH))

    def tearDown(self):
        self.list = None
        self.ctx.destroy()
        self.ctx = None

    def test_list_attrs(self):
        self.assertIsInstance(self.list, SList)
        self.assertEqual(self.list.nodetype(), SNode.LIST)
        self.assertEqual(self.list.keyword(), "list")

        self.assertEqual(self.list.schema_path(), self.SCHEMA_PATH)

        self.assertEqual(self.list.data_path(), self.DATA_PATH)
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

    def test_rpc_params(self):
        leaf = next(self.rpc.children())
        self.assertIsInstance(leaf, SLeaf)
        self.assertEqual(leaf.data_path(), "/yolo-system:format-disk/disk")
        leaf = next(self.rpc.input().children())
        self.assertIsInstance(leaf, SLeaf)

    def test_rpc_no_parent(self):
        self.assertIsNone(self.rpc.parent())


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
        # mod = t.module()
        # self.assertIsNot(mod, None)
        # self.assertEqual(mod.name(), "wtf-types")

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

    def test_leaf_type_union(self):
        leaf = next(self.ctx.find_path("/yolo-system:conf/yolo-system:number"))
        self.assertIsInstance(leaf, SLeafList)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), "types:number")
        self.assertEqual(t.base(), Type.UNION)
        types = set(u.name() for u in t.union_types())
        self.assertEqual(types, set(["int16", "int32", "uint16", "uint32"]))
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
