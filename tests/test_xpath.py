# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import copy
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

    def test_xpath_get(self):
        for xpath, value, defval, expected in XPATH_GET_EXPECTED_RESULTS:
            res = ly.xpath_get(DICT, xpath, defval)
            if expected:
                self.assertEqual(res, value)
                self.assertNotEqual(res, defval)
            else:
                self.assertNotEqual(res, value)
                self.assertEqual(res, defval)

    def test_xpath_set(self):
        d = copy.deepcopy(DICT)
        ly.xpath_set(d, "/val", 43)
        ly.xpath_set(d, "/cont1/leaf1", "foo")
        ly.xpath_set(d, "/cont1/leaf2", "bar")
        ly.xpath_set(d, "/iface[name='eth0']", {"name": "eth0", "up": False})
        ly.xpath_set(d, "/iface[name='eth1']/ipv4/address[ip='10.0.0.2']/mtu", 1500)
        ly.xpath_set(
            d,
            "/iface[name='eth1']/ipv6/address[ip='3ffe::ffff'][prefixlen='100']",
            {"ip": "3ffe::ffff", "prefixlen": 100, "tentative": False},
        )
        ly.xpath_set(d, "/lstnum[.='100']", 100)
        ly.xpath_set(d, "/lstnum[.='1']", 1, after="")
        with self.assertRaises(ValueError):
            ly.xpath_set(d, "/lstnum[.='1000']", 1000, after="1000000")
        with self.assertRaises(ValueError):
            ly.xpath_set(
                d,
                "/iface[name='eth1']/ipv4/address[ip='10.0.0.3']",
                {"ip": "10.0.0.3"},
                after="[ip='10.0.0.55']",
            )
        ly.xpath_set(
            d, "/iface[name='eth1']/ipv4/address[ip='10.0.0.3']", {"ip": "10.0.0.3"}
        )
        ly.xpath_set(d, "/cont2/newlist[foo='bar']", {"foo": "bar", "name": "baz"})
        ly.xpath_set(d, "/cont2/newll[.='12']", 12)
        self.assertEqual(
            d,
            {
                "cont1": {"leaf1": "foo", "leaf2": "bar"},
                "cont2": {
                    "leaf2": "coucou2",
                    "newlist": [{"foo": "bar", "name": "baz"}],
                    "newll": [12],
                },
                "iface": [
                    {"name": "eth0", "up": False},
                    {
                        "name": "eth1",
                        "ipv4": {
                            "address": [
                                {"ip": "10.0.0.2", "mtu": 1500},
                                {"ip": "10.0.0.6"},
                                {"ip": "10.0.0.3"},
                            ]
                        },
                        "ipv6": {
                            "address": [
                                {
                                    "ip": "3ffe::321:8",
                                    "prefixlen": 64,
                                    "tentative": False,
                                },
                                {
                                    "ip": "3ffe::ff12",
                                    "prefixlen": 96,
                                    "tentative": True,
                                },
                                {
                                    "ip": "3ffe::ffff",
                                    "prefixlen": 100,
                                    "tentative": False,
                                },
                            ]
                        },
                    },
                ],
                "iface2": [
                    {"name": "eth2", "mtu": 1500},
                    {"name": "eth3", "mtu": 1000},
                ],
                "lst2": ["a", "b", "c"],
                "lstnum": [1, 10, 20, 30, 40, 100],
                "val": 43,
            },
        )


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

DICT = {
    "cont1": {"leaf1": "coucou1",},
    "cont2": {"leaf2": "coucou2",},
    "iface": [
        {
            "name": "eth0",
            "ipv4": {"address": [{"ip": "10.0.0.1"}, {"ip": "10.0.0.153"},],},
            "ipv6": {"address": [{"ip": "3ffe::123:1"}, {"ip": "3ffe::c00:c00"},],},
        },
        {
            "name": "eth1",
            "ipv4": {
                "address": ly.KeyedList(
                    [{"ip": "10.0.0.2"}, {"ip": "10.0.0.6"},], key_name="ip",
                ),
            },
            "ipv6": {
                "address": ly.KeyedList(
                    [
                        {"ip": "3ffe::321:8", "prefixlen": 64, "tentative": False},
                        {"ip": "3ffe::ff12", "prefixlen": 96, "tentative": True},
                    ],
                    key_name=("ip", "prefixlen"),
                ),
            },
        },
    ],
    "iface2": ly.KeyedList(
        [{"name": "eth2", "mtu": 1500}, {"name": "eth3", "mtu": 1000}], key_name="name"
    ),
    "lst2": ["a", "b", "c"],
    "lstnum": [10, 20, 30, 40],
    "val": 42,
}

XPATH_GET_EXPECTED_RESULTS = [
    ("/val", 42, None, True),
    ("val", 42, None, True),
    ("lst2", ["a", "b", "c"], None, True),
    (
        "iface[name='eth0']/ipv4/address",
        [{"ip": "10.0.0.1"}, {"ip": "10.0.0.153"}],
        None,
        True,
    ),
    (
        "/iface[name='eth1']/ipv6/address[ip='3ffe::321:8'][prefixlen='64']",
        {"ip": "3ffe::321:8", "prefixlen": 64, "tentative": False},
        None,
        True,
    ),
    ("cont1/leaf1", "coucou1", None, True),
    ("cont2/leaf2", "coucou2", None, True),
    ("cont1/leaf2", "not found", "fallback", False),
    ("cont1/leaf2", "not found", None, False),
]
