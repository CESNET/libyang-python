# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import json
import os
import unittest
from unittest import mock
from unittest.mock import patch

from _libyang import lib
from libyang import (
    Context,
    DAnyxml,
    DataType,
    DContainer,
    DLeaf,
    DNode,
    DNotif,
    DRpc,
    IOType,
    LibyangError,
)


YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


# -------------------------------------------------------------------------------------
class DataTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        modules = [
            self.ctx.load_module("ietf-netconf"),
            self.ctx.load_module("yolo-system"),
        ]

        for mod in modules:
            mod.feature_enable_all()

    def tearDown(self):
        self.ctx.destroy()
        self.ctx = None

    JSON_CONFIG = """{
  "yolo-system:conf": {
    "hostname": "foo",
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "path": "/CESNET/libyang-python",
        "enabled": false
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html",
        "enabled": true
      }
    ],
    "number": [
      1000,
      2000,
      3000
    ],
    "speed": 1234
  }
}
"""

    def test_data_parse_config_json(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", no_state=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json", with_siblings=True)
            self.assertEqual(j, self.JSON_CONFIG)
        finally:
            dnode.free()

    JSON_CONFIG_WITH_STATE = """{
  "yolo-system:state": {
    "speed": 4321
  },
  "yolo-system:conf": {
    "hostname": "foo",
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "path": "/CESNET/libyang-python",
        "enabled": false
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html",
        "enabled": true
      }
    ],
    "number": [
      1000,
      2000,
      3000
    ],
    "speed": 1234
  }
}
"""

    def test_data_parse_config_json_without_yang_lib(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json")
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json", with_siblings=True)
            self.assertEqual(j, self.JSON_CONFIG_WITH_STATE)
        finally:
            dnode.free()

    JSON_CONFIG_ADD_LIST_ITEM = """{
  "yolo-system:conf": {
    "hostname": "foo",
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "path": "/CESNET/libyang-python",
        "enabled": false
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html",
        "enabled": true
      },
      {
        "proto": "http",
        "host": "barfoo.com",
        "path": "/barfoo/index.html"
      }
    ],
    "number": [
      1000,
      2000,
      3000
    ],
    "speed": 1234
  }
}
"""

    def test_data_add_path(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", no_state=True)
        dnode.new_path(
            '/yolo-system:conf/url[host="barfoo.com"][proto="http"]/path',
            "/barfoo/index.html",
        )
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json", with_siblings=True)
            self.assertEqual(j, self.JSON_CONFIG_ADD_LIST_ITEM)
        finally:
            dnode.free()

    JSON_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "data/config.json")

    def test_data_parse_config_json_file(self):
        with open(self.JSON_CONFIG_FILE, encoding="utf-8") as f:
            dnode = self.ctx.parse_data_file(f, "json", no_state=True)
        self.assertIsInstance(dnode, DContainer)
        dnode.free()

        with open(self.JSON_CONFIG_FILE, encoding="utf-8") as f:
            dnode = self.ctx.parse_data(
                "json", in_data=f, in_type=IOType.FILE, no_state=True
            )
        self.assertIsInstance(dnode, DContainer)
        dnode.free()

        dnode = self.ctx.parse_data(
            "json",
            in_data=self.JSON_CONFIG_FILE,
            in_type=IOType.FILEPATH,
            no_state=True,
        )
        self.assertIsInstance(dnode, DContainer)
        dnode.free()

    JSON_STATE = """{
  "yolo-system:state": {
    "hostname": "foo",
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "path": "/CESNET/libyang-python",
        "enabled": false
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html",
        "enabled": true
      }
    ],
    "number": [
      1000,
      2000,
      3000
    ],
    "speed": 1234
  }
}
"""

    def test_data_parse_state_json(self):
        dnode = self.ctx.parse_data_mem(self.JSON_STATE, "json", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json", with_siblings=True)
            self.assertEqual(j, self.JSON_STATE)
        finally:
            dnode.free()

    XML_CONFIG = """<conf xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <path>/CESNET/libyang-python</path>
    <enabled>false</enabled>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
    <enabled>true</enabled>
  </url>
  <number>1000</number>
  <number>2000</number>
  <number>3000</number>
  <speed>1234</speed>
</conf>
"""

    def test_data_parse_config_xml(self):
        dnode = self.ctx.parse_data_mem(self.XML_CONFIG, "xml", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.print_mem("xml", with_siblings=True, trim_default_values=True)
            self.assertEqual(xml, self.XML_CONFIG)
        finally:
            dnode.free()

    XML_CONFIG_MULTI_ERROR = """<conf xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <url>
    <proto>https</proto>
    <path>/CESNET/libyang-python</path>
    <enabled>abcd</enabled>
  </url>
  <number>2000</number>
</conf>
"""

    def test_data_parse_config_xml_multi_error(self):
        with self.assertRaises(Exception) as cm:
            self.ctx.parse_data_mem(
                self.XML_CONFIG_MULTI_ERROR,
                "xml",
                validate_present=True,
                validate_multi_error=True,
            )
        self.assertEqual(
            str(cm.exception),
            'failed to parse data tree: Invalid boolean value "abcd".: '
            'List instance is missing its key "host".',
        )

    XML_STATE = """<state xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <path>/CESNET/libyang-python</path>
    <enabled>false</enabled>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
    <enabled>true</enabled>
  </url>
  <number>1000</number>
  <number>2000</number>
  <number>3000</number>
  <speed>1234</speed>
</state>
"""

    def test_data_parse_data_xml(self):
        dnode = self.ctx.parse_data_mem(self.XML_STATE, "xml", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.print("xml", out_type=IOType.MEMORY, with_siblings=True)
            self.assertEqual(xml, self.XML_STATE)
        finally:
            dnode.free()

    XML_NETCONF_IN = """<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <edit-config>
              <target>
                <running/>
              </target>
              <config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <conf xmlns="urn:yang:yolo:system">
                    <hostname-ref>notdefined</hostname-ref>
                </conf>
              </config>
            </edit-config>
            </rpc>
            """

    XML_NETCONF_OUT = """<edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <target>
    <running/>
  </target>
  <config>
    <conf xmlns="urn:yang:yolo:system">
      <hostname-ref>notdefined</hostname-ref>
    </conf>
  </config>
</edit-config>
"""

    def test_data_parse_netconf(self):
        dnode = self.ctx.parse_op_mem("xml", self.XML_NETCONF_IN, DataType.RPC_NETCONF)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.print("xml", out_type=IOType.MEMORY)
            self.assertEqual(xml, self.XML_NETCONF_OUT)
        finally:
            dnode.free()

    ANYMXML = """<format-disk xmlns="urn:yang:yolo:system">
      <html-info>
        <p xmlns="http://www.w3.org/1999/xhtml">
        </p>
      </html-info>
</format-disk>
"""

    def test_data_parse_anyxml(self):
        dnode = self.ctx.parse_op_mem("xml", self.ANYMXML, dtype=DataType.RPC_YANG)
        dnode = dnode.find_path("/yolo-system:format-disk/html-info")
        self.assertIsInstance(dnode, DAnyxml)

    def test_data_create_paths(self):
        state = self.ctx.create_data_path("/yolo-system:state")
        try:
            state.create_path("hostname", "foo")
            state.create_path("speed", 1234)
            state.create_path("number", 1000)
            state.create_path("number", 2000)
            state.create_path("number", 3000)
            u = state.create_path('url[proto="https"][host="github.com"]')
            u.create_path("path", "/CESNET/libyang-python")
            u.create_path("enabled", False)
            u = state.create_path('url[proto="http"][host="foobar.com"]')
            u.create_path("port", 8080)
            u.create_path("path", "/index.html")
            u.create_path("enabled", True)
            self.assertEqual(state.print_mem("json"), self.JSON_STATE)
        finally:
            state.free()

    def test_data_create_invalid_type(self):
        s = self.ctx.create_data_path("/yolo-system:state")
        try:
            with self.assertRaises(LibyangError):
                s.create_path("speed", 1234000000000000000000000000)
        finally:
            s.free()

    def test_data_create_invalid_regexp(self):
        s = self.ctx.create_data_path("/yolo-system:state")
        try:
            with self.assertRaises(LibyangError):
                s.create_path("hostname", "INVALID.HOST")
        finally:
            s.free()

    DICT_CONFIG = {
        "conf": {
            "hostname": "foo",
            "speed": 1234,
            "number": [1000, 2000, 3000],
            "url": [
                {
                    "enabled": False,
                    "path": "/CESNET/libyang-python",
                    "host": "github.com",
                    "proto": "https",
                },
                {
                    "port": 8080,
                    "proto": "http",
                    "path": "/index.html",
                    "enabled": True,
                    "host": "foobar.com",
                },
            ],
        }
    }

    def test_data_to_dict_config(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            dic = dnode.print_dict()
        finally:
            dnode.free()
        self.assertEqual(dic, self.DICT_CONFIG)

    def test_data_to_dict_rpc_input(self):
        in_data = '{"yolo-system:format-disk": {"disk": "/dev/sda"}}'
        dnode = self.ctx.parse_op_mem("json", in_data, DataType.RPC_YANG)
        self.assertIsInstance(dnode, DRpc)
        try:
            dic = dnode.print_dict()
        finally:
            dnode.free()
        self.assertEqual(dic, {"format-disk": {"disk": "/dev/sda"}})

    def test_data_from_dict_module(self):
        module = self.ctx.get_module("yolo-system")
        dnode = module.parse_data_dict(
            self.DICT_CONFIG, strict=True, validate_present=True
        )
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json")
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))

    def test_data_from_dict_module_free_func(self):
        module = self.ctx.get_module("yolo-system")

        free_func = mock.Mock()
        dnode = module.parse_data_dict(
            self.DICT_CONFIG, strict=True, validate_present=True
        )
        dnode.free_func = free_func
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json")
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))
        free_func.assert_called()

    DICT_CONFIG_WITH_PREFIX = {
        "yolo-system:conf": {
            "hostname": "foo",
            "speed": 1234,
            "number": [1000, 2000, 3000],
            "url": [
                {
                    "enabled": False,
                    "path": "/CESNET/libyang-python",
                    "host": "github.com",
                    "proto": "https",
                },
                {
                    "port": 8080,
                    "proto": "http",
                    "path": "/index.html",
                    "enabled": True,
                    "host": "foobar.com",
                },
            ],
        }
    }

    def test_data_from_dict_module_with_prefix(self):
        module = self.ctx.get_module("yolo-system")
        dnode = module.parse_data_dict(
            self.DICT_CONFIG_WITH_PREFIX, strict=True, validate_present=True
        )
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json")
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))

    def test_data_from_dict_invalid(self):
        module = self.ctx.get_module("yolo-system")

        created = []
        freed = []

        class FakeLib:
            def __init__(self, orig):
                self.orig = orig

            def lyd_new_inner(self, *args):
                ret = self.orig.lyd_new_inner(*args)
                c = args[4][0]
                if ret == lib.LY_SUCCESS:
                    created.append(c)
                return ret

            def lyd_new_term(self, *args):
                ret = self.orig.lyd_new_term(*args)
                c = args[5][0]
                if ret == lib.LY_SUCCESS:
                    created.append(c)
                return ret

            def lyd_new_list(self, *args):
                ret = self.orig.lyd_new_list(*args)
                c = args[4][0]
                if ret == lib.LY_SUCCESS:
                    created.append(c)
                return ret

            def lyd_free_tree(self, dnode):
                freed.append(dnode)
                self.orig.lyd_free_tree(dnode)

            def __getattr__(self, name):
                return getattr(self.orig, name)

        fake_lib = FakeLib(lib)
        root = module.parse_data_dict(
            {"conf": {"hostname": "foo", "speed": 1234, "number": [1000, 2000, 3000]}},
            strict=True,
            validate_present=True,
        )
        invalid_dict = {
            "url": [
                {
                    "host": "github.com",
                    "proto": "https",
                    "enabled": False,
                    "path": "/CESNET/libyang-python",
                },
                {
                    "proto": "http",
                    "path": "/index.html",
                    "enabled": True,
                    "host": "foobar.com",
                    "port": "INVALID.PORT",
                },
            ]
        }

        try:
            with patch("libyang.data.lib", fake_lib):
                with self.assertRaises(LibyangError):
                    root.merge_data_dict(
                        invalid_dict, strict=True, validate_present=True
                    )

            self.assertGreater(len(created), 0)
            self.assertGreater(len(freed), 0)
            self.assertEqual(freed, list(reversed(created)))
        finally:
            root.free()

    def test_data_from_dict_container(self):
        dnode = self.ctx.create_data_path("/yolo-system:conf")
        self.assertIsInstance(dnode, DContainer)
        subtree = dnode.merge_data_dict(
            self.DICT_CONFIG["conf"], strict=True, validate_present=True
        )
        # make sure subtree validation is forbidden
        with self.assertRaises(LibyangError):
            subtree.validate(validate_present=True)
        try:
            dnode.validate(validate_present=True)
            j = dnode.print_mem("json")
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))

    def test_data_from_dict_leaf(self):
        dnode = self.ctx.create_data_path("/yolo-system:state")
        self.assertIsInstance(dnode, DContainer)
        dnode.merge_data_dict(
            {"hostname": "foo"}, strict=True, validate=True, validate_present=True
        )
        try:
            j = dnode.print_mem("json", pretty=False, trim_default_values=True)
        finally:
            dnode.free()
        self.assertEqual(j, '{"yolo-system:state":{"hostname":"foo"}}')

    def test_data_from_dict_rpc(self):
        dnode = self.ctx.create_data_path("/yolo-system:format-disk")
        self.assertIsInstance(dnode, DRpc)
        dnode.merge_data_dict(
            {"duration": 42},
            strict=True,
            validate=True,
            rpcreply=True,
        )
        try:
            j = dnode.print_mem("json", pretty=False)
        finally:
            dnode.free()
        self.assertEqual(j, '{"yolo-system:format-disk":{"duration":42}}')

    def test_data_from_dict_action(self):
        module = self.ctx.get_module("yolo-system")
        dnode = module.parse_data_dict(
            {
                "conf": {
                    "url": [
                        {
                            "proto": "https",
                            "host": "github.com",
                            "fetch": {"timeout": 42},
                        },
                    ],
                },
            },
            strict=True,
            rpc=True,
        )
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem("json")
        finally:
            dnode.free()
        self.assertEqual(
            j,
            """{
  "yolo-system:conf": {
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "fetch": {
          "timeout": 42
        }
      }
    ]
  }
}
""",
        )

    def test_data_to_dict_action(self):
        module = self.ctx.get_module("yolo-system")
        request = module.parse_data_dict(
            {
                "conf": {
                    "url": [
                        {
                            "proto": "https",
                            "host": "github.com",
                            "fetch": {"timeout": 42},
                        },
                    ],
                },
            },
            strict=True,
            rpc=True,
        )
        request = request.find_path(
            "/yolo-system:conf/url[proto='https'][host='github.com']/fetch"
        )
        dnode = self.ctx.parse_op_mem(
            "json",
            '{"yolo-system:result":"not found"}',
            dtype=DataType.REPLY_YANG,
            parent=request,
        )
        try:
            dic = dnode.print_dict()
        finally:
            request.free()

        self.assertEqual(
            dic,
            {
                "conf": {
                    "url": [
                        {
                            "proto": "https",
                            "host": "github.com",
                            "fetch": {
                                "result": "not found",
                                "timeout": 42,  # probably bug in linyang, this is part of input
                            },
                        },
                    ],
                },
            },
        )

    DICT_NOTIF = {
        "alarm-triggered": {"description": "An error occurred", "severity": 3}
    }

    JSON_NOTIF = """{
  "yolo-system:alarm-triggered": {
    "description": "An error occurred",
    "severity": 3
  }
}
"""

    def test_notification_from_dict_module(self):
        module = self.ctx.get_module("yolo-system")
        dnotif = module.parse_data_dict(self.DICT_NOTIF, strict=True, notification=True)
        self.assertIsInstance(dnotif, DNotif)
        try:
            j = dnotif.print_mem("json")
        finally:
            dnotif.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_NOTIF))

    DICT_NOTIF_KEYLESS_LIST = {
        "config-change": {"edit": [{"target": "a"}, {"target": "b"}]},
    }

    def test_data_to_dict_keyless_list(self):
        module = self.ctx.get_module("yolo-system")
        dnotif = module.parse_data_dict(
            self.DICT_NOTIF_KEYLESS_LIST, strict=True, notification=True
        )
        self.assertIsInstance(dnotif, DNotif)
        try:
            dic = dnotif.print_dict()
        finally:
            dnotif.free()
        self.assertEqual(dic, self.DICT_NOTIF_KEYLESS_LIST)

    XML_DIFF_STATE1 = """<state xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <speed>1234</speed>
  <number>1000</number>
  <number>2000</number>
  <number>3000</number>
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <path>/CESNET/libyang-python</path>
    <enabled>false</enabled>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
    <enabled>true</enabled>
  </url>
</state>
"""
    XML_DIFF_STATE2 = """<state xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <speed>5432</speed>
  <number>1000</number>
  <number>3000</number>
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <path>/CESNET/libyang-python</path>
    <enabled>true</enabled>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
    <enabled>false</enabled>
  </url>
  <url>
    <proto>ftp</proto>
    <host>github.com</host>
    <path>/CESNET/libyang-python</path>
    <enabled>false</enabled>
  </url>
</state>
"""

    XML_DIFF_RESULT = """<state xmlns="urn:yang:yolo:system" xmlns:yang="urn:ietf:params:xml:ns:yang:1" yang:operation="none">
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <enabled yang:operation="replace" yang:orig-default="false" yang:orig-value="false">true</enabled>
  </url>
  <url yang:operation="none">
    <proto>http</proto>
    <host>foobar.com</host>
    <enabled yang:operation="replace" yang:orig-default="false" yang:orig-value="true">false</enabled>
  </url>
  <url yang:operation="create">
    <proto>ftp</proto>
    <host>github.com</host>
    <path>/CESNET/libyang-python</path>
    <enabled>false</enabled>
  </url>
  <number yang:operation="delete" yang:orig-position="1">2000</number>
  <speed yang:operation="replace" yang:orig-default="false" yang:orig-value="1234">5432</speed>
</state>
"""

    def test_data_diff(self):
        dnode1 = self.ctx.parse_data_mem(
            self.XML_DIFF_STATE1, "xml", validate_present=True
        )
        self.assertIsInstance(dnode1, DContainer)
        dnode2 = self.ctx.parse_data_mem(
            self.XML_DIFF_STATE2, "xml", validate_present=True
        )
        self.assertIsInstance(dnode2, DContainer)

        result = dnode1.diff(dnode2)
        self.assertEqual(result.print_mem("xml"), self.XML_DIFF_RESULT)
        dnode1.free()
        dnode2.free()

    TREE = [
        "/yolo-system:conf",
        "/yolo-system:conf/hostname",
        "/yolo-system:conf/url[proto='https'][host='github.com']",
        "/yolo-system:conf/url[proto='https'][host='github.com']/proto",
        "/yolo-system:conf/url[proto='https'][host='github.com']/host",
        "/yolo-system:conf/url[proto='https'][host='github.com']/path",
        "/yolo-system:conf/url[proto='https'][host='github.com']/enabled",
        "/yolo-system:conf/url[proto='http'][host='foobar.com']",
        "/yolo-system:conf/url[proto='http'][host='foobar.com']/proto",
        "/yolo-system:conf/url[proto='http'][host='foobar.com']/host",
        "/yolo-system:conf/url[proto='http'][host='foobar.com']/port",
        "/yolo-system:conf/url[proto='http'][host='foobar.com']/path",
        "/yolo-system:conf/url[proto='http'][host='foobar.com']/enabled",
        "/yolo-system:conf/number[.='1000']",
        "/yolo-system:conf/number[.='2000']",
        "/yolo-system:conf/number[.='3000']",
        "/yolo-system:conf/speed",
    ]

    def test_iter_tree(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        try:
            paths = [d.path() for d in dnode.iter_tree()]
            self.assertEqual(paths, self.TREE)
        finally:
            dnode.free()

    def test_find_one(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            hostname = dnode.find_one("hostname")
            self.assertIsInstance(hostname, DNode)
            self.assertEqual(hostname.name(), "hostname")
        finally:
            dnode.free()

    def test_find_all(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            urls = dnode.find_all("url")
            urls = list(urls)
            self.assertEqual(len(urls), 2)

            expected_url = {
                "url": [
                    {
                        "proto": "https",
                        "host": "github.com",
                        "path": "/CESNET/libyang-python",
                        "enabled": False,
                    }
                ]
            }
            self.assertEqual(urls[0].print_dict(absolute=False), expected_url)
        finally:
            dnode.free()

    def test_add_defaults(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        node = dnode.find_path("/yolo-system:conf/speed")
        self.assertIsInstance(node, DLeaf)
        node.free(with_siblings=False)
        node = dnode.find_path("/yolo-system:conf/speed")
        self.assertIsNone(node)
        dnode.add_defaults()
        node = dnode.find_path("/yolo-system:conf/speed")
        self.assertIsInstance(node, DLeaf)
        self.assertEqual(node.value(), 4321)

    def test_dnode_double_free(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        dnode.free()
        dnode.free()

    def test_dnode_unlink(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, "json", validate_present=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            child = dnode.find_one("hostname")
            self.assertIsInstance(child, DNode)
            child.unlink(with_siblings=False)
            self.assertIsNone(dnode.find_one("hostname"))
            child = next(dnode.children(), None)
            self.assertIsNot(child, None)
            child.unlink(with_siblings=True)
            child = next(dnode.children(), None)
            self.assertIsNone(child, None)
        finally:
            dnode.free()
