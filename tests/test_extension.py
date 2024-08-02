# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import logging
import os
from typing import Optional
import unittest

from libyang import (
    Context,
    ExtensionCompiled,
    ExtensionParsed,
    ExtensionPlugin,
    LibyangError,
    LibyangExtensionError,
    Module,
)


YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


# -------------------------------------------------------------------------------------
class TestExtensionPlugin(ExtensionPlugin):
    def __init__(self, context: Context) -> None:
        super().__init__(
            "omg-extensions",
            "type-desc",
            "omg-extensions-type-desc-plugin-v1",
            context,
            parse_clb=self._parse_clb,
            compile_clb=self._compile_clb,
            parse_free_clb=self._parse_free_clb,
            compile_free_clb=self._compile_free_clb,
        )
        self.parse_clb_called = 0
        self.compile_clb_called = 0
        self.parse_free_clb_called = 0
        self.compile_free_clb_called = 0
        self.parse_clb_exception: Optional[LibyangExtensionError] = None
        self.compile_clb_exception: Optional[LibyangExtensionError] = None
        self.parse_parent_stmt = None

    def reset(self) -> None:
        self.parse_clb_called = 0
        self.compile_clb_called = 0
        self.parse_free_clb_called = 0
        self.compile_free_clb_called = 0
        self.parse_clb_exception = None
        self.compile_clb_exception = None

    def _parse_clb(self, module: Module, ext: ExtensionParsed) -> None:
        self.parse_clb_called += 1
        if self.parse_clb_exception is not None:
            raise self.parse_clb_exception
        self.parse_substmts(ext)
        self.parse_parent_stmt = self.stmt2str(ext.cdata.parent_stmt)

    def _compile_clb(self, pext: ExtensionParsed, cext: ExtensionCompiled) -> None:
        self.compile_clb_called += 1
        if self.compile_clb_exception is not None:
            raise self.compile_clb_exception
        self.compile_substmts(pext, cext)

    def _parse_free_clb(self, ext: ExtensionParsed) -> None:
        self.parse_free_clb_called += 1
        self.free_parse_substmts(ext)

    def _compile_free_clb(self, ext: ExtensionCompiled) -> None:
        self.compile_free_clb_called += 1
        self.free_compile_substmts(ext)


# -------------------------------------------------------------------------------------
class ExtensionTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.plugin = TestExtensionPlugin(self.ctx)

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    def test_extension_basic(self):
        self.ctx.load_module("yolo-system")
        self.assertEqual(5, self.plugin.parse_clb_called)
        self.assertEqual(6, self.plugin.compile_clb_called)
        self.assertEqual(0, self.plugin.parse_free_clb_called)
        self.assertEqual(0, self.plugin.compile_free_clb_called)
        self.assertEqual("type", self.plugin.parse_parent_stmt)
        self.ctx.destroy()
        self.assertEqual(5, self.plugin.parse_clb_called)
        self.assertEqual(6, self.plugin.compile_clb_called)
        self.assertEqual(5, self.plugin.parse_free_clb_called)
        self.assertEqual(6, self.plugin.compile_free_clb_called)

    def test_extension_invalid_parse(self):
        self.plugin.parse_clb_exception = LibyangExtensionError(
            "this extension cannot be parsed",
            self.plugin.ERROR_NOT_VALID,
            logging.ERROR,
        )
        with self.assertRaises(LibyangError):
            self.ctx.load_module("yolo-system")

    def test_extension_invalid_compile(self):
        self.plugin.compile_clb_exception = LibyangExtensionError(
            "this extension cannot be compiled",
            self.plugin.ERROR_NOT_VALID,
            logging.ERROR,
        )
        with self.assertRaises(LibyangError):
            self.ctx.load_module("yolo-system")
