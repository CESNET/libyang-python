# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák

import unittest

from _libyang import ffi, lib
from libyang.data import DNode, DContainer
from libyang.context import Context
from libyang.schema_compiled import SCContainer


class TestGenericDataNode(unittest.TestCase):

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lyd_node *")
        self.tested_type = DNode(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_schema(self):
        # empty
        self.assertIsNone(self.tested_type.schema)

        # non-empty
        snode = ffi.new("struct lysc_node *")
        snode.nodetype = lib.LYS_CONTAINER
        self.tested_ctype.schema = snode
        self.assertTrue(self.tested_type.schema._cdata, self.tested_ctype.schema)
        self.assertTrue(isinstance(self.tested_type.schema, SCContainer))

    def test_parent(self):
        # empty
        self.assertIsNone(self.tested_type.parent)

        # non-empty
        parent = ffi.new("struct lyd_node_inner *")
        scparent = ffi.new("struct lysc_node *")
        scparent.nodetype = lib.LYS_CONTAINER
        parent.schema = scparent
        self.tested_ctype.parent = parent
        self.assertTrue(self.tested_type.parent._cdata, parent)
        self.assertTrue(isinstance(self.tested_type.parent, DContainer))

    def test_name(self):
        # empty
        sc = ffi.new("struct lysc_node *")
        self.tested_ctype.schema = sc

        self.assertIsNone(self.tested_type.name)

        # non-empty
        empty_name = ffi.new("char[]", b"")
        sc.nodetype = lib.LYS_CONTAINER
        sc.name = empty_name
        self.assertTrue(self.tested_type.name == "")
        self.assertTrue(isinstance(self.tested_type.name, str))

        nep_name = ffi.new("char[]", b"aaaa")
        sc.name = nep_name
        self.assertTrue(self.tested_type.name == "aaaa")
        self.assertTrue(isinstance(self.tested_type.name, str))

    def test_metadata(self):
        # empty
        gen = self.tested_type.metadata()
        self.assertRaises(StopIteration, next, gen)

        # non-empty
        meta0 = ffi.new("struct lyd_meta *")
        meta1 = ffi.new("struct lyd_meta *")
        meta0.next = meta1
        self.tested_ctype.meta = meta0

        gen = self.tested_type.metadata()
        item = next(gen)
        self.assertTrue(meta0 == item._cdata)
        item = next(gen)
        self.assertTrue(meta1 == item._cdata)
        self.assertRaises(StopIteration, next, gen)




