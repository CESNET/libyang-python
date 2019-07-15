# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import unittest

from libyang import Context
from libyang.schema import Container
from libyang.schema import Extension
from libyang.schema import Leaf
from libyang.schema import LeafList
from libyang.schema import List
from libyang.schema import Module
from libyang.schema import Node
from libyang.schema import Rpc
from libyang.schema import Type


YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang')


#------------------------------------------------------------------------------
class ModuleTest(unittest.TestCase):

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.module = self.ctx.load_module('yolo-system')

    def tearDown(self):
        self.module = None
        self.ctx = None

    def test_mod_dump_str(self):
        s = str(self.module)
        self.assertGreater(len(s), 0)

    def test_mod_attrs(self):
        self.assertEqual(self.module.name(), 'yolo-system')
        self.assertEqual(self.module.description(), 'YOLO.')
        self.assertEqual(self.module.prefix(), 'sys')

    def test_mod_iter(self):
        children = list(iter(self.module))
        self.assertEqual(len(children), 4)

    def test_mod_children_rpcs(self):
        rpcs = list(self.module.children(types=(Node.RPC,)))
        self.assertEqual(len(rpcs), 2)

    def test_mod_features(self):
        self.assertFalse(self.module.feature_state('turbo-boost'))
        self.module.feature_enable('turbo-boost')
        self.assertTrue(self.module.feature_state('turbo-boost'))
        self.module.feature_disable('turbo-boost')
        self.assertFalse(self.module.feature_state('turbo-boost'))
        self.module.feature_enable_all()
        self.assertTrue(self.module.feature_state('turbo-boost'))
        self.module.feature_disable_all()


#------------------------------------------------------------------------------
class ContainerTest(unittest.TestCase):

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        mod = self.ctx.load_module('yolo-system')
        mod.feature_enable_all()
        self.container = next(self.ctx.find_path('/yolo-system:conf'))

    def tearDown(self):
        self.container = None
        self.ctx = None

    def test_cont_attrs(self):
        self.assertIsInstance(self.container, Container)
        self.assertEqual(self.container.nodetype(), Node.CONTAINER)
        self.assertEqual(self.container.keyword(), 'container')
        self.assertEqual(self.container.name(), 'conf')
        self.assertEqual(self.container.fullname(), 'yolo-system:conf')
        self.assertEqual(self.container.description(), 'Configuration.')
        self.assertEqual(self.container.config_set(), False)
        self.assertEqual(self.container.config_false(), False)
        self.assertEqual(self.container.mandatory(), False)
        self.assertIsInstance(self.container.module(), Module)
        self.assertEqual(self.container.schema_path(), '/yolo-system:conf')
        self.assertEqual(self.container.data_path(), '/yolo-system:conf')
        self.assertIs(self.container.presence(), None)

    def test_cont_iter(self):
        children = list(iter(self.container))
        self.assertEqual(len(children), 6)

    def test_cont_children_leafs(self):
        leafs = list(self.container.children(types=(Node.LEAF,)))
        self.assertEqual(len(leafs), 4)


#------------------------------------------------------------------------------
class ListTest(unittest.TestCase):

    SCHEMA_PATH = '/yolo-system:conf/yolo-system:url'
    DATA_PATH = "/yolo-system:conf/url[proto='%s'][host='%s']"

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module('yolo-system')
        self.list = next(self.ctx.find_path(self.SCHEMA_PATH))

    def tearDown(self):
        self.list = None
        self.ctx = None

    def test_list_attrs(self):
        self.assertIsInstance(self.list, List)
        self.assertEqual(self.list.nodetype(), Node.LIST)
        self.assertEqual(self.list.keyword(), 'list')
        self.assertEqual(self.list.schema_path(), self.SCHEMA_PATH)
        self.assertEqual(self.list.data_path(), self.DATA_PATH)
        self.assertFalse(self.list.ordered())

    def test_list_keys(self):
        keys = list(self.list.keys())
        self.assertEqual(len(keys), 2)

    def test_list_iter(self):
        children = list(iter(self.list))
        self.assertEqual(len(children), 4)

    def test_list_children_skip_keys(self):
        children = list(self.list.children(skip_keys=True))
        self.assertEqual(len(children), 2)


#------------------------------------------------------------------------------
class RpcTest(unittest.TestCase):

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module('yolo-system')
        self.rpc = next(self.ctx.find_path('/yolo-system:format-disk'))

    def tearDown(self):
        self.rpc = None
        self.ctx = None

    def test_rpc_attrs(self):
        self.assertIsInstance(self.rpc, Rpc)
        self.assertEqual(self.rpc.nodetype(), Node.RPC)
        self.assertEqual(self.rpc.keyword(), 'rpc')
        self.assertEqual(self.rpc.schema_path(), '/yolo-system:format-disk')

    def test_rpc_extensions(self):
        ext = list(self.rpc.extensions())
        self.assertEqual(len(ext), 1)
        ext = self.rpc.get_extension('require-admin', prefix='omg-extensions')
        self.assertIsInstance(ext, Extension)

    def test_rpc_params(self):
        leaf = next(self.rpc.children())
        self.assertIsInstance(leaf, Leaf)
        self.assertEqual(leaf.data_path(), '/yolo-system:format-disk/disk')
        leaf = next(self.rpc.input().children())
        self.assertIsInstance(leaf, Leaf)


#------------------------------------------------------------------------------
class LeafTypeTest(unittest.TestCase):

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        self.ctx.load_module('yolo-system')

    def tearDown(self):
        self.ctx = None

    def test_leaf_type_derived(self):
        leaf = next(self.ctx.find_path('/yolo-system:conf/yolo-system:hostname'))
        self.assertIsInstance(leaf, Leaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), 'host')
        self.assertEqual(t.base(), Type.STRING)
        d = t.derived_type()
        self.assertEqual(d.name(), 'str')
        dd = d.derived_type()
        self.assertEqual(dd.name(), 'string')

    def test_leaf_type_status(self):
        leaf = next(self.ctx.find_path('/yolo-system:conf/yolo-system:hostname'))
        self.assertIsInstance(leaf, Leaf)
        self.assertEqual(leaf.deprecated(), False)
        self.assertEqual(leaf.obsolete(), False)
        leaf = next(self.ctx.find_path('/yolo-system:conf/yolo-system:deprecated-leaf'))
        self.assertIsInstance(leaf, Leaf)
        self.assertEqual(leaf.deprecated(), True)
        self.assertEqual(leaf.obsolete(), False)
        leaf = next(self.ctx.find_path('/yolo-system:conf/yolo-system:obsolete-leaf'))
        self.assertIsInstance(leaf, Leaf)
        self.assertEqual(leaf.deprecated(), False)
        self.assertEqual(leaf.obsolete(), True)

    def test_leaf_type_union(self):
        leaf = next(self.ctx.find_path('/yolo-system:conf/yolo-system:number'))
        self.assertIsInstance(leaf, LeafList)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), 'number')
        self.assertEqual(t.base(), Type.UNION)
        types = set(u.name() for u in t.union_types())
        self.assertEqual(types, set(['signed', 'unsigned']))
        bases = set(t.basenames())
        self.assertEqual(bases, set(['int16', 'int32', 'uint16', 'uint32']))

    def test_leaf_type_enum(self):
        leaf = next(self.ctx.find_path(
            '/yolo-system:conf/yolo-system:url/yolo-system:proto'))
        self.assertIsInstance(leaf, Leaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), 'protocol')
        self.assertEqual(t.base(), Type.ENUM)
        enums = [e for e, _ in t.enums()]
        self.assertEqual(enums, ['http', 'https', 'ftp', 'sftp', 'tftp'])

    def test_leaf_type_bits(self):
        leaf = next(self.ctx.find_path(
            '/yolo-system:chmod/yolo-system:input/yolo-system:perms'))
        self.assertIsInstance(leaf, Leaf)
        t = leaf.type()
        self.assertIsInstance(t, Type)
        self.assertEqual(t.name(), 'permissions')
        self.assertEqual(t.base(), Type.BITS)
        bits = [b for b, _ in t.bits()]
        self.assertEqual(bits, ['read', 'write', 'execute'])
