# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import Context
from libyang.schema import Module
from libyang.schema import Rpc
from libyang.util import LibyangError


YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang')


#------------------------------------------------------------------------------
class ContextTest(unittest.TestCase):

    def test_ctx_no_dir(self):
        ctx = Context()
        self.assertIsNot(ctx, None)

    def test_ctx_dir(self):
        ctx = Context(YANG_DIR)
        self.assertIsNot(ctx, None)

    def test_ctx_invalid_dir(self):
        ctx = Context('/does/not/exist')
        self.assertIsNot(ctx, None)

    def test_ctx_missing_dir(self):
        ctx = Context(os.path.join(YANG_DIR, 'yolo'))
        self.assertIsNot(ctx, None)
        with self.assertRaises(LibyangError):
            ctx.load_module('yolo-system')

    def test_ctx_env_search_dir(self):
        try:
            os.environ['YANGPATH'] = ':'.join([
                os.path.join(YANG_DIR, 'omg'),
                os.path.join(YANG_DIR, 'wtf'),
                ])
            ctx = Context(os.path.join(YANG_DIR, 'yolo'))
            mod = ctx.load_module('yolo-system')
            self.assertIsInstance(mod, Module)
        finally:
            del os.environ['YANGPATH']

    def test_ctx_load_module(self):
        ctx = Context(YANG_DIR)
        mod = ctx.load_module('yolo-system')
        self.assertIsInstance(mod, Module)

    def test_ctx_get_module(self):
        ctx = Context(YANG_DIR)
        ctx.load_module('yolo-system')
        mod = ctx.get_module('wtf-types')
        self.assertIsInstance(mod, Module)

    def test_ctx_get_invalid_module(self):
        ctx = Context(YANG_DIR)
        ctx.load_module('wtf-types')
        with self.assertRaises(LibyangError):
            ctx.get_module('yolo-system')

    def test_ctx_load_invalid_module(self):
        ctx = Context(YANG_DIR)
        with self.assertRaises(LibyangError):
            ctx.load_module('invalid-module')

    def test_ctx_find_path(self):
        ctx = Context(YANG_DIR)
        ctx.load_module('yolo-system')
        node = next(ctx.find_path('/yolo-system:format-disk'))
        self.assertIsInstance(node, Rpc)

    def test_ctx_iter_modules(self):
        ctx = Context(YANG_DIR)
        ctx.load_module('yolo-system')
        modules = list(iter(ctx))
        self.assertGreater(len(modules), 0)
