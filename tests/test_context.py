# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import Context, LibyangError, Module, SLeaf, SLeafList
from libyang.util import c2str


YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


# -------------------------------------------------------------------------------------


class ContextTest(unittest.TestCase):
    def test_ctx_no_dir(self):
        with Context() as ctx:
            self.assertIsNot(ctx, None)

    def test_ctx_yanglib(self):
        ctx = Context(YANG_DIR, yanglib_path=YANG_DIR + "/yang-library.json")
        ctx.load_module("yolo-system")
        dnode = ctx.get_yanglib_data()
        j = dnode.print_mem("json", with_siblings=True)
        self.assertIsInstance(j, str)

    def test_ctx_dir(self):
        with Context(YANG_DIR) as ctx:
            self.assertIsNot(ctx, None)

    def test_ctx_duplicate_searchpath(self):
        duplicate_search_path = ":".join([YANG_DIR, YANG_DIR])
        try:
            Context(duplicate_search_path)
        except LibyangError:
            self.fail("Context.__init__ should not raise LibyangError")

    def test_ctx_invalid_dir(self):
        with Context("/does/not/exist") as ctx:
            self.assertIsNot(ctx, None)

    def test_ctx_missing_dir(self):
        with Context(os.path.join(YANG_DIR, "yolo")) as ctx:
            self.assertIsNot(ctx, None)
            with self.assertRaises(LibyangError):
                ctx.load_module("yolo-system")

    def test_ctx_env_search_dir(self):
        try:
            os.environ["YANGPATH"] = ":".join(
                [os.path.join(YANG_DIR, "omg"), os.path.join(YANG_DIR, "wtf")]
            )
            with Context(os.path.join(YANG_DIR, "yolo")) as ctx:
                mod = ctx.load_module("yolo-system")
                self.assertIsInstance(mod, Module)
        finally:
            del os.environ["YANGPATH"]

    def test_ctx_load_module(self):
        with Context(YANG_DIR) as ctx:
            mod = ctx.load_module("yolo-system")
            self.assertIsInstance(mod, Module)

    def test_ctx_get_module(self):
        with Context(YANG_DIR) as ctx:
            ctx.load_module("yolo-system")
            mod = ctx.get_module("wtf-types")
            self.assertIsInstance(mod, Module)

    def test_ctx_get_invalid_module(self):
        with Context(YANG_DIR) as ctx:
            ctx.load_module("wtf-types")
            with self.assertRaises(LibyangError):
                ctx.get_module("yolo-system")

    def test_ctx_load_invalid_module(self):
        with Context(YANG_DIR) as ctx:
            with self.assertRaises(LibyangError):
                ctx.load_module("invalid-module")

    def test_ctx_find_path(self):
        with Context(YANG_DIR) as ctx:
            ctx.load_module("yolo-system")
            node = next(ctx.find_path("/yolo-system:conf/offline"))
            self.assertIsInstance(node, SLeaf)
            node2 = next(ctx.find_path("../number", root_node=node))
            self.assertIsInstance(node2, SLeafList)

    def test_ctx_iter_modules(self):
        with Context(YANG_DIR) as ctx:
            ctx.load_module("yolo-system")
            modules = list(iter(ctx))
            self.assertGreater(len(modules), 0)

    YOLO_MOD_PATH = os.path.join(YANG_DIR, "yolo/yolo-system.yang")

    def test_ctx_parse_module(self):
        with open(self.YOLO_MOD_PATH, encoding="utf-8") as f:
            mod_str = f.read()
        with Context(YANG_DIR) as ctx:
            mod = ctx.parse_module_str(mod_str, features=["turbo-boost", "networking"])
            self.assertIsInstance(mod, Module)

        with open(self.YOLO_MOD_PATH, encoding="utf-8") as f:
            with Context(YANG_DIR) as ctx:
                mod = ctx.parse_module_file(f, features=["turbo-boost", "networking"])
                self.assertIsInstance(mod, Module)

    def test_ctx_leafref_extended(self):
        with Context(YANG_DIR, leafref_extended=True) as ctx:
            mod = ctx.load_module("yolo-leafref-extended")
            self.assertIsInstance(mod, Module)

    def test_context_dict(self):
        with Context(YANG_DIR) as ctx:
            orig_str = "teststring"
            handle = ctx.add_to_dict(orig_str)
            self.assertEqual(orig_str, c2str(handle))
            ctx.remove_from_dict(orig_str)

    def test_ctx_disable_searchdirs(self):
        with Context(YANG_DIR, disable_searchdirs=True) as ctx:
            with self.assertRaises(LibyangError):
                ctx.load_module("yolo-nodetypes")

    def test_ctx_using_clb(self):
        def get_module_valid_clb(mod_name, *_):
            YOLO_NODETYPES_MOD_PATH = os.path.join(YANG_DIR, "yolo/yolo-nodetypes.yang")
            self.assertEqual(mod_name, "yolo-nodetypes")
            with open(YOLO_NODETYPES_MOD_PATH, encoding="utf-8") as f:
                mod_str = f.read()
            return "yang", mod_str

        def get_module_invalid_clb(mod_name, *_):
            return None

        with Context(YANG_DIR, disable_searchdirs=True) as ctx:
            with self.assertRaises(LibyangError):
                ctx.load_module("yolo-nodetypes")

            ctx.external_module_loader.set_module_data_clb(get_module_invalid_clb)
            with self.assertRaises(LibyangError):
                mod = ctx.load_module("yolo-nodetypes")

            ctx.external_module_loader.set_module_data_clb(get_module_valid_clb)
            mod = ctx.load_module("yolo-nodetypes")
            self.assertIsInstance(mod, Module)
