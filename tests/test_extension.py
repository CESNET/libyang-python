# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import logging
import os
from typing import Any, Optional
import unittest

from libyang import (
    Context,
    ExtensionCompiled,
    ExtensionParsed,
    ExtensionPlugin,
    LibyangError,
    LibyangExtensionError,
    Module,
    PLeaf,
    SLeaf,
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


# -------------------------------------------------------------------------------------
class ExampleParseExtensionPlugin(ExtensionPlugin):
    def __init__(self, context: Context) -> None:
        super().__init__(
            "omg-extensions",
            "parse-validation",
            "omg-extensions-parse-validation-plugin-v1",
            context,
            parse_clb=self._parse_clb,
        )

    def _verify_single(self, parent: Any) -> None:
        count = 0
        for e in parent.extensions():
            if e.name() == self.name and e.module().name() == self.module_name:
                count += 1
            if count > 1:
                raise LibyangExtensionError(
                    f"Extension {self.name} is allowed to be defined just once per given "
                    "parent node context.",
                    self.ERROR_NOT_VALID,
                    logging.ERROR,
                )

    def _parse_clb(self, _, ext: ExtensionParsed) -> None:
        parent = ext.parent_node()
        if not isinstance(parent, PLeaf):
            raise LibyangExtensionError(
                f"Extension {ext.name()} is allowed only in leaf nodes",
                self.ERROR_NOT_VALID,
                logging.ERROR,
            )
        self._verify_single(parent)
        # here you put code to perform something reasonable actions you need for your extension


class ExampleCompileExtensionPlugin(ExtensionPlugin):
    def __init__(self, context: Context) -> None:
        super().__init__(
            "omg-extensions",
            "compile-validation",
            "omg-extensions-compile-validation-plugin-v1",
            context,
            compile_clb=self._compile_clb,
        )

    def _compile_clb(self, pext: ExtensionParsed, cext: ExtensionCompiled) -> None:
        parent = cext.parent_node()
        if not isinstance(parent, SLeaf):
            raise LibyangExtensionError(
                f"Extension {cext.name()} is allowed only in leaf nodes",
                self.ERROR_NOT_VALID,
                logging.ERROR,
            )
        # here you put code to perform something reasonable actions you need for your extension


class ExtensionExampleTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.plugins = []

    def tearDown(self):
        self.plugins.clear()
        self.ctx.destroy()
        self.ctx = None

    def test_parse_validation_example(self):
        self.plugins.append(ExampleParseExtensionPlugin(self.ctx))
        self.ctx.load_module("yolo-system")

    def test_compile_validation_example(self):
        self.plugins.append(ExampleParseExtensionPlugin(self.ctx))
        self.plugins.append(ExampleCompileExtensionPlugin(self.ctx))
        with self.assertRaises(LibyangError):
            self.ctx.load_module("yolo-system")
