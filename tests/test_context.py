# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import Context, LibyangError, Module, SRpc

YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


# -------------------------------------------------------------------------------------
class ContextTest(unittest.TestCase):
    def test_ctx_no_dir(self):
        with Context() as ctx:
            self.assertIsNot(ctx, None)

    def test_ctx_dir(self):
        with Context(YANG_DIR) as ctx:
            self.assertIsNot(ctx, None)

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
            node = next(ctx.find_path("/yolo-system:format-disk"))
            self.assertIsInstance(node, SRpc)

    def test_ctx_iter_modules(self):
        with Context(YANG_DIR) as ctx:
            ctx.load_module("yolo-system")
            modules = list(iter(ctx))
            self.assertGreater(len(modules), 0)

    YOLO_MOD_PATH = './tests/yang/yolo/yolo-system.yang'

    def test_ctx_parse_module(self):
        with open(self.YOLO_MOD_PATH) as f:
            mod_str = f.read()
        with Context(YANG_DIR) as ctx:
            mod = ctx.parse_module_str(mod_str, features=['turbo-boost', 'networking'])
            self.assertIsInstance(mod, Module)

        with open(self.YOLO_MOD_PATH) as f:
            with Context(YANG_DIR) as ctx:
                mod = ctx.parse_module_file(f, features=['turbo-boost', 'networking'])
                self.assertIsInstance(mod, Module)
