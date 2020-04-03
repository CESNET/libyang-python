# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import json
import os
import unittest

from libyang import Context
from libyang import LibyangError
from libyang.data import DContainer
from libyang.data import ParserOpt
from libyang.data import PrintFmt
from libyang.data import PrintOpt
from libyang.data import dict_to_dnode
from libyang.data import dnode_to_dict


YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang')


#------------------------------------------------------------------------------
class DataTest(unittest.TestCase):

    def setUp(self):
        self.ctx = Context(YANG_DIR)
        mod = self.ctx.load_module('yolo-system')
        mod.feature_enable_all()

    def tearDown(self):
        self.ctx = None

    JSON_CONFIG = '''{
  "yolo-system:conf": {
    "hostname": "foo",
    "speed": 1234,
    "number": [
      1000,
      2000,
      3000
    ],
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "path": "/rjarry/libyang-cffi"
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html"
      }
    ]
  }
}
'''

    def test_data_parse_config_json(self):
        dnode = self.ctx.parse_data_str(
            self.JSON_CONFIG, PrintFmt.JSON, ParserOpt.CONFIG)
        self.assertIsInstance(dnode, DContainer)
        j = dnode.dump_str(PrintFmt.JSON, PrintOpt.PRETTY)
        self.assertEqual(j, self.JSON_CONFIG)
        dnode.free()

    JSON_STATE = '''{
  "yolo-system:state": {
    "hostname": "foo",
    "speed": 1234,
    "number": [
      1000,
      2000,
      3000
    ],
    "url": [
      {
        "proto": "https",
        "host": "github.com",
        "path": "/rjarry/libyang-cffi"
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html"
      }
    ]
  }
}
'''

    def test_data_parse_state_json(self):
        dnode = self.ctx.parse_data_str(
            self.JSON_STATE, PrintFmt.JSON,
            ParserOpt.DATA | ParserOpt.NO_YANGLIB)
        self.assertIsInstance(dnode, DContainer)
        j = dnode.dump_str(PrintFmt.JSON, PrintOpt.PRETTY)
        self.assertEqual(j, self.JSON_STATE)
        dnode.free()

    XML_CONFIG = '''<conf xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <speed>1234</speed>
  <number>1000</number>
  <number>2000</number>
  <number>3000</number>
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <path>/rjarry/libyang-cffi</path>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
  </url>
</conf>
'''

    def test_data_parse_config_xml(self):
        dnode = self.ctx.parse_data_str(
            self.XML_CONFIG, PrintFmt.XML, ParserOpt.CONFIG)
        self.assertIsInstance(dnode, DContainer)
        xml = dnode.dump_str(PrintFmt.XML, PrintOpt.PRETTY)
        self.assertEqual(xml, self.XML_CONFIG)
        dnode.free()

    XML_STATE = '''<state xmlns="urn:yang:yolo:system">
  <hostname>foo</hostname>
  <speed>1234</speed>
  <number>1000</number>
  <number>2000</number>
  <number>3000</number>
  <url>
    <proto>https</proto>
    <host>github.com</host>
    <path>/rjarry/libyang-cffi</path>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
  </url>
</state>
'''

    def test_data_parse_data_xml(self):
        dnode = self.ctx.parse_data_str(
            self.XML_STATE, PrintFmt.XML,
            ParserOpt.DATA | ParserOpt.NO_YANGLIB)
        self.assertIsInstance(dnode, DContainer)
        xml = dnode.dump_str(PrintFmt.XML, PrintOpt.PRETTY)
        self.assertEqual(xml, self.XML_STATE)
        dnode.free()

    def test_data_create_paths(self):
        state = self.ctx.create_data_path('/yolo-system:state')
        state.create_path('hostname', 'foo')
        state.create_path('speed', 1234)
        state.create_path('number', 1000)
        state.create_path('number', 2000)
        state.create_path('number', 3000)
        u = state.create_path('url[proto="https"][host="github.com"]')
        u.create_path('path', '/rjarry/libyang-cffi')
        u = state.create_path('url[proto="http"][host="foobar.com"]')
        u.create_path('port', 8080)
        u.create_path('path', '/index.html')
        state.validate(ParserOpt.STRICT)
        self.assertEqual(state.dump_str(PrintFmt.JSON, PrintOpt.PRETTY), self.JSON_STATE)
        state.free()

    def test_data_create_invalid_type(self):
        s = self.ctx.create_data_path('/yolo-system:state')
        with self.assertRaises(LibyangError):
            s.create_path('speed', 1234000000000000000000000000)
        s.free()

    def test_data_create_invalid_regexp(self):
        s = self.ctx.create_data_path('/yolo-system:state')
        with self.assertRaises(LibyangError):
            s.create_path('hostname', 'INVALID.HOST')
        s.free()

    DICT_CONFIG = {
        'conf': {
            'hostname': 'foo',
            'speed': 1234,
            'number': [1000, 2000, 3000],
            'url': [
                {
                    'proto': 'https',
                    'host': 'github.com',
                    'path': '/rjarry/libyang-cffi',
                },
                {
                    'proto': 'http',
                    'host': 'foobar.com',
                    'port': 8080,
                    'path': '/index.html',
                },
            ],
        },
    }

    def test_data_to_dict(self):
        dnode = self.ctx.parse_data_str(
            self.JSON_CONFIG, PrintFmt.JSON, ParserOpt.CONFIG)
        self.assertIsInstance(dnode, DContainer)
        dic = dnode_to_dict(dnode)
        dnode.free()
        self.assertEqual(dic, self.DICT_CONFIG)

    def test_data_from_dict(self):
        schema = self.ctx.get_module('yolo-system')
        dnode = dict_to_dnode(self.DICT_CONFIG, schema)
        j = dnode.dump_str(PrintFmt.JSON, PrintOpt.PRETTY)
        dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))
