# Copyright (c) 2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

from libyang import (
    BaseTypeAdded,
    BaseTypeRemoved,
    Context,
    DefaultAdded,
    EnumRemoved,
    EnumStatusAdded,
    EnumStatusRemoved,
    NodeTypeAdded,
    NodeTypeRemoved,
    SNodeAdded,
    SNodeRemoved,
    StatusAdded,
    StatusRemoved,
    schema_diff,
)


OLD_YANG_DIR = os.path.join(os.path.dirname(__file__), "yang-old")
NEW_YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


# -------------------------------------------------------------------------------------
class DiffTest(unittest.TestCase):
    expected_diffs = frozenset(
        (
            (BaseTypeAdded, "/yolo-system:conf/speed"),
            (BaseTypeAdded, "/yolo-system:state/speed"),
            (BaseTypeRemoved, "/yolo-system:conf/speed"),
            (BaseTypeRemoved, "/yolo-system:state/speed"),
            (DefaultAdded, "/yolo-system:conf/speed"),
            (DefaultAdded, "/yolo-system:state/speed"),
            (NodeTypeAdded, "/yolo-system:conf/number"),
            (NodeTypeAdded, "/yolo-system:state/number"),
            (NodeTypeRemoved, "/yolo-system:conf/number"),
            (NodeTypeRemoved, "/yolo-system:state/number"),
            (SNodeAdded, "/yolo-system:conf/full"),
            (SNodeAdded, "/yolo-system:state/full"),
            (SNodeAdded, "/yolo-system:conf/hostname-ref"),
            (SNodeAdded, "/yolo-system:conf/url/enabled"),
            (SNodeAdded, "/yolo-system:conf/url/fetch"),
            (
                SNodeAdded,
                "/yolo-system:conf/url/fetch/input/timeout",
            ),
            (
                SNodeAdded,
                "/yolo-system:conf/url/fetch/output/result",
            ),
            (SNodeAdded, "/yolo-system:state/hostname-ref"),
            (SNodeAdded, "/yolo-system:state/url/enabled"),
            (SNodeAdded, "/yolo-system:state/url/fetch"),
            (
                SNodeAdded,
                "/yolo-system:state/url/fetch/input/timeout",
            ),
            (
                SNodeAdded,
                "/yolo-system:state/url/fetch/output/result",
            ),
            (StatusAdded, "/yolo-system:conf/deprecated-leaf"),
            (StatusAdded, "/yolo-system:conf/obsolete-leaf"),
            (StatusAdded, "/yolo-system:state/deprecated-leaf"),
            (StatusAdded, "/yolo-system:state/obsolete-leaf"),
            (StatusRemoved, "/yolo-system:conf/deprecated-leaf"),
            (StatusRemoved, "/yolo-system:conf/obsolete-leaf"),
            (StatusRemoved, "/yolo-system:state/deprecated-leaf"),
            (StatusRemoved, "/yolo-system:state/obsolete-leaf"),
            (SNodeAdded, "/yolo-system:alarm-triggered"),
            (SNodeAdded, "/yolo-system:alarm-triggered/severity"),
            (SNodeAdded, "/yolo-system:alarm-triggered/description"),
            (SNodeAdded, "/yolo-system:config-change"),
            (SNodeAdded, "/yolo-system:config-change/edit"),
            (SNodeAdded, "/yolo-system:config-change/edit/target"),
            (EnumRemoved, "/yolo-system:conf/url/proto"),
            (EnumRemoved, "/yolo-system:state/url/proto"),
            (EnumStatusAdded, "/yolo-system:conf/url/proto"),
            (EnumStatusAdded, "/yolo-system:state/url/proto"),
            (EnumStatusRemoved, "/yolo-system:conf/url/proto"),
            (EnumStatusRemoved, "/yolo-system:state/url/proto"),
            (SNodeAdded, "/yolo-system:conf/pill/red/out"),
            (SNodeAdded, "/yolo-system:state/pill/red/out"),
            (SNodeAdded, "/yolo-system:conf/pill/blue/in"),
            (SNodeAdded, "/yolo-system:state/pill/blue/in"),
            (SNodeAdded, "/yolo-system:alarm-triggered/severity"),
            (SNodeAdded, "/yolo-system:alarm-triggered/description"),
        )
    )

    def test_diff(self):
        with Context(OLD_YANG_DIR) as ctx_old, Context(NEW_YANG_DIR) as ctx_new:
            mod = ctx_old.load_module("yolo-system")
            mod.feature_enable_all()
            mod = ctx_new.load_module("yolo-system")
            mod.feature_enable_all()
            diffs = []
            for d in schema_diff(ctx_old, ctx_new):
                if isinstance(d, (SNodeAdded, SNodeRemoved)):
                    diffs.append((d.__class__, d.node.schema_path()))
                else:
                    diffs.append((d.__class__, d.new.schema_path()))

            self.assertEqual(frozenset(diffs), self.expected_diffs)
