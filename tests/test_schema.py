# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák

import unittest

from libyang2 import Context


class TestContext(unittest.TestCase):
    def test_primitive_getters(self):
        with Context() as ctx:
            testmod = """
                <module xmlns="urn:ietf:params:xml:ns:yang:yin:1" name="mod">
                <yang-version value="1.1"/>
                <namespace uri="ns"/>
                <prefix value="pref"/>
                <organization><text>org</text></organization>
                <contact><text>contact</text></contact>
                <description><text>desc</text></description>
                <reference><text>ref</text></reference>
                <revision date="2019-02-02"/>
            </module>
            """
            mod = ctx.parse_module(testmod, fmt="yin")
            self.assertEqual(mod.name, "mod")
            self.assertEqual(mod.revision, "2019-02-02")
            self.assertEqual(mod.namespace, "ns")
            self.assertEqual(mod.prefix, "pref")
            self.assertEqual(mod.filepath, None)
            self.assertEqual(mod.organization, "org")
            self.assertEqual(mod.contact, "contact")
            self.assertEqual(mod.description, "desc")
            self.assertEqual(mod.reference, "ref")
            self.assertEqual(mod.implemented, True)
