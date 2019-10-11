# Copyright (c) 2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import Context
from libyang.diff import BaseTypeAdded
from libyang.diff import BaseTypeRemoved
from libyang.diff import StatusChanged
from libyang.diff import schema_diff


OLD_YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang-old')
NEW_YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang')


#------------------------------------------------------------------------------
class DiffTest(unittest.TestCase):

    expected_diffs = frozenset((
        (BaseTypeAdded, '/yolo-system:conf/yolo-system:speed'),
        (BaseTypeAdded, '/yolo-system:state/yolo-system:speed'),
        (BaseTypeRemoved, '/yolo-system:conf/yolo-system:speed'),
        (BaseTypeRemoved, '/yolo-system:state/yolo-system:speed'),
        (StatusChanged, '/yolo-system:conf/yolo-system:deprecated-leaf'),
        (StatusChanged, '/yolo-system:conf/yolo-system:obsolete-leaf'),
        (StatusChanged, '/yolo-system:state/yolo-system:deprecated-leaf'),
        (StatusChanged, '/yolo-system:state/yolo-system:obsolete-leaf'),
    ))

    def test_diff(self):
        ctx_old = Context(OLD_YANG_DIR)
        mod = ctx_old.load_module('yolo-system')
        mod.feature_enable_all()
        ctx_new = Context(NEW_YANG_DIR)
        mod = ctx_new.load_module('yolo-system')
        mod.feature_enable_all()
        diffs = frozenset((d.__class__, d.new.schema_path())
                          for d in schema_diff(ctx_old, ctx_new))
        self.assertEqual(diffs, self.expected_diffs)
