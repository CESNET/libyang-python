# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák

import unittest
import os

from _libyang import lib

from libyang import Context
from libyang.log import LibyangError

MODULES_DIR = os.path.join(os.path.dirname(__file__), "modules")

# při přidávání modulu
# feature se dá změnit, když uděláš z imported modulu implementovanej modul

class TestContext(unittest.TestCase):
    def testConstruction(self):
        with Context() as ctx:
            self.assertIsNotNone(ctx)

    def testOptions(self):
        with Context(allimplemented=True) as ctx:
            self.assertIsNotNone(ctx)
            self.assertTrue(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_ALL_IMPLEMENTED
            )
            self.assertTrue(ctx.allimplemented)
            ctx.allimplemented = False
            self.assertFalse(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_ALL_IMPLEMENTED
            )
            self.assertFalse(ctx.allimplemented)

        with Context(disable_searchdir_cwd=True) as ctx:
            self.assertIsNotNone(ctx)
            self.assertTrue(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_DISABLE_SEARCHDIR_CWD
            )
            self.assertTrue(ctx.disable_searchdir_cwd)
            ctx.disable_searchdir_cwd = False
            self.assertFalse(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_DISABLE_SEARCHDIR_CWD
            )
            self.assertFalse(ctx.disable_searchdir_cwd)

        with Context(disable_searchdirs=True) as ctx:
            self.assertIsNotNone(ctx)
            self.assertTrue(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_DISABLE_SEARCHDIRS
            )
            self.assertTrue(ctx.disable_searchdirs)
            ctx.disable_searchdirs = False
            self.assertFalse(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_DISABLE_SEARCHDIRS
            )
            self.assertFalse(ctx.disable_searchdirs)

        with Context(noyanglibrary=True) as ctx:
            self.assertIsNotNone(ctx)
            self.assertTrue(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_NO_YANGLIBRARY
            )
            self.assertTrue(ctx.noyanglibrary)
            self.assertRaises(AttributeError, setattr, ctx, "noyanglibrary", False)

        with Context(prefer_searchdirs=True) as ctx:
            self.assertIsNotNone(ctx)
            self.assertTrue(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_PREFER_SEARCHDIRS
            )
            self.assertTrue(ctx.prefer_searchdirs)
            ctx.prefer_searchdirs = False
            self.assertFalse(
                lib.ly_ctx_get_options(ctx._cdata) & lib.LY_CTX_PREFER_SEARCHDIRS
            )
            self.assertFalse(ctx.prefer_searchdirs)

    def testSearchdirs(self):
        with Context() as ctx:
            ctx.searchdirs.add("/tmp")
            self.assertTrue("/tmp" in ctx.searchdirs)
            self.assertFalse("/hom" in ctx.searchdirs)
            ctx.searchdirs.add("/tmp")
            self.assertTrue("/tmp" in ctx.searchdirs)
            ctx.searchdirs.remove("/tmp")
            self.assertFalse("/tmp" in ctx.searchdirs)
            ctx.searchdirs.add("/tmp")
            controlset = set()
            self.assertFalse(controlset == ctx.searchdirs)
            for item in ctx.searchdirs:
                controlset.add(item)
            self.assertTrue(controlset == ctx.searchdirs)
            controlset = set()
            self.assertFalse(controlset == ctx.searchdirs)
            for item in ctx.searchdirs:
                controlset.add(item)
            self.assertTrue(controlset == ctx.searchdirs)

        with Context(searchdirs=["/tmp", "/etc"]) as ctx:
            self.assertTrue("/tmp" in ctx.searchdirs)
            self.assertTrue("/etc" in ctx.searchdirs)

        with Context(searchdirs=("/tmp", "/etc")) as ctx:
            self.assertTrue("/tmp" in ctx.searchdirs)
            self.assertTrue("/etc" in ctx.searchdirs)

        with Context(searchdirs=("/tmp", "/etc")) as ctx:
            self.assertRaises(KeyError, ctx.searchdirs.remove, "aa")
            self.assertEqual("{'/tmp', '/etc'}", str(ctx.searchdirs))

        with Context(searchdirs=("/tmp", "/etc")) as ctx:
            self.assertTrue("/tmp" in ctx.searchdirs and "/etc" in ctx.searchdirs)
            self.assertEqual(len(ctx.searchdirs), 2)
            ctx.searchdirs.clear()
            self.assertEqual(len(ctx.searchdirs), 0)
            ctx.searchdirs.update(("/tmp", "/etc"))
            self.assertEqual(len(ctx.searchdirs), 2)
            self.assertTrue(ctx.searchdirs.isdisjoint(("aa", "bb")))
            self.assertFalse(ctx.searchdirs.isdisjoint(("aa", "bb", "/tmp")))

    def test_parse_module(self):
        with open(os.path.join(MODULES_DIR, "testmod.yang"), "r") as yangfile:
            testmodyang = yangfile.read()

        with open(os.path.join(MODULES_DIR, "testmodyin.yin"), "r") as yinfile:
            testmodyin = yinfile.read()

        with Context() as ctx:
            modyin = ctx.parse_module(testmodyin, fmt="yin")
            self.assertTrue(modyin)
            modyang = ctx.parse_module(testmodyang, fmt="yang")
            self.assertTrue(modyang)
            self.assertRaises(LibyangError, ctx.parse_module, testmodyin)
            self.assertRaises(LibyangError, ctx.parse_module, testmodyang, "yin")

            with open(os.path.join(MODULES_DIR, "testmodyin.yin"), "r") as yinfile:
                with open(os.path.join(MODULES_DIR, "testmod.yang"), "r") as yangfile:
                    with Context() as ctx:
                        modyin = ctx.parse_module(yinfile, fmt="yin")
                        self.assertTrue(modyin)
                        modyang = ctx.parse_module(yangfile, fmt="yang")
                        self.assertTrue(modyang)
                        self.assertRaises(LibyangError, ctx.parse_module, yinfile)
                        self.assertRaises(
                            LibyangError, ctx.parse_module, yangfile, "yin"
                        )

    def test_load_module(self):
        with Context(searchdirs=[MODULES_DIR]) as ctx:
            mod = ctx.load_module("testmod")
            self.assertTrue(mod)

        with Context() as ctx:
            self.assertRaises(LibyangError, ctx.load_module, "testmod")

    def test_get_modules(self):
        with Context(searchdirs=[MODULES_DIR]) as ctx:
            mod = ctx.load_module("testmod")
            self.assertTrue(mod)

            for module in ctx:
                pass

    def test_reset_latest(self):
        with Context(searchdirs=[MODULES_DIR]) as ctx:
            ctx.reset_latest()
            mod = ctx.load_module("testmod")
            self.assertTrue(mod)
            ctx.reset_latest()
