# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import unittest

import libyang as ly


# -------------------------------------------------------------------------------------
class XPathTest(unittest.TestCase):
    def test_xpath_split(self):
        for xpath, split_result in XPATH_SPLIT_EXPECTED_RESULTS.items():
            if split_result is ValueError:
                with self.assertRaises(split_result):
                    list(ly.xpath_split(xpath))
            else:
                self.assertEqual(list(ly.xpath_split(xpath)), split_result)


XPATH_SPLIT_EXPECTED_RESULTS = {
    "": ValueError,
    "/p:nam": [("p", "nam", [])],
    "/nam1/nam2": [(None, "nam1", []), (None, "nam2", [])],
    "/nam1/p:nam2": [(None, "nam1", []), ("p", "nam2", [])],
    '/p:nam/lst[k1="foo"]': [("p", "nam", []), (None, "lst", [("k1", "foo")])],
    '/p:nam/lst[.="foo"]': [("p", "nam", []), (None, "lst", [(".", "foo")])],
    "/nam/p:lst[k1='foo'][k2='bar']/x": [
        (None, "nam", []),
        ("p", "lst", [("k1", "foo"), ("k2", "bar")]),
        (None, "x", []),
    ],
    "/nam/p:lst[k1='=:[/]\\'']/l2[k2=\"dead::beef/64\"]": [
        (None, "nam", []),
        ("p", "lst", [("k1", "=:[/]'")]),
        (None, "l2", [("k2", "dead::beef/64")]),
    ],
    "foo": [(None, "foo", [])],
    "foo/bar": [(None, "foo", []), (None, "bar", [])],
    "//invalid/xpath": ValueError,
    "/xxx[abc='2']invalid:xx/xpath": ValueError,
}
