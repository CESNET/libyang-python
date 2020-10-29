# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import unittest

import libyang as ly


# -------------------------------------------------------------------------------------
class KeyedListTest(unittest.TestCase):
    def test_keylist_base(self):
        l = ly.KeyedList(["x"])
        with self.assertRaises(TypeError):
            l.index("x")
        with self.assertRaises(TypeError):
            l.insert(0, "x")
        with self.assertRaises(TypeError):
            l.reverse()
        with self.assertRaises(TypeError):
            l.sort()
        with self.assertRaises(TypeError):
            l["x"] = 2
        with self.assertRaises(TypeError):
            l[0]  # pylint: disable=pointless-statement
        with self.assertRaises(TypeError):
            del l[0]
        with self.assertRaises(TypeError):
            l.pop()
        with self.assertRaises(TypeError):
            l.pop(0)

    def test_keylist_leaflist(self):
        l = ly.KeyedList("abcdef")
        self.assertEqual(len(l), 6)
        self.assertIn("e", l)
        l.remove("e")
        self.assertNotIn("e", l)
        self.assertIn("c", l)
        del l["c"]
        self.assertNotIn("c", l)
        with self.assertRaises(KeyError):
            del l["x"]
        with self.assertRaises(KeyError):
            l.remove("x")
        self.assertEqual(l.pop("x", "not-found"), "not-found")
        self.assertEqual(l.pop("b"), "b")
        self.assertNotIn("b", l)
        l.clear()
        self.assertEqual(len(l), 0)
        self.assertEqual(l, [])

    def test_keylist_list_one_key(self):
        l = ly.KeyedList(
            [
                {"mtu": 1500, "name": "eth0"},
                {"mtu": 512, "name": "eth2"},
                {"mtu": 1280, "name": "eth4"},
            ],
            key_name="name",
        )
        self.assertIn("eth2", l)
        self.assertEqual(l["eth4"], {"mtu": 1280, "name": "eth4"})
        del l["eth0"]
        self.assertEqual(
            l, [{"mtu": 512, "name": "eth2"}, {"mtu": 1280, "name": "eth4"}]
        )
        l.append({"name": "eth6", "mtu": 6})
        l.append({"name": "eth5", "mtu": 5})
        l.append({"name": "eth10", "mtu": 10})
        self.assertEqual(
            l,
            # order does not matter
            [
                {"mtu": 10, "name": "eth10"},
                {"mtu": 512, "name": "eth2"},
                {"mtu": 5, "name": "eth5"},
                {"mtu": 6, "name": "eth6"},
                {"mtu": 1280, "name": "eth4"},
            ],
        )
        self.assertEqual(l.pop("eth10000", {}), {})
        self.assertEqual(l.pop("eth10"), {"mtu": 10, "name": "eth10"})
        self.assertNotIn("eth10", l)
        l.clear()
        self.assertEqual(len(l), 0)
        self.assertEqual(l, [])

    def test_keylist_list_multiple_keys(self):
        l = ly.KeyedList(
            [
                {"id": 5, "size": 10, "desc": "foo"},
                {"id": 8, "size": 5, "desc": "bar"},
                {"id": 2, "size": 14, "desc": "baz"},
            ],
            key_name=("id", "size"),
        )
        self.assertIn(("8", "5"), l)
        self.assertEqual(l["8", "5"], {"id": 8, "size": 5, "desc": "bar"})
        self.assertEqual(l[("2", "14")], {"id": 2, "size": 14, "desc": "baz"})
        del l["2", "14"]
        self.assertEqual(
            l,
            [{"id": 5, "size": 10, "desc": "foo"}, {"id": 8, "size": 5, "desc": "bar"}],
        )
        l.clear()
        self.assertEqual(len(l), 0)
        self.assertEqual(l, [])
