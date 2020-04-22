# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import json
import os
import unittest

from libyang import Context
from libyang import LibyangError
from libyang.data import DContainer
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
        self.ctx.destroy()
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
        "path": "/rjarry/libyang-cffi",
        "enabled": false
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html",
        "enabled": true
      }
    ]
  }
}
'''

    def test_data_parse_config_json(self):
        dnode = self.ctx.parse_data_str(self.JSON_CONFIG, 'json', config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.dump_str('json', pretty=True)
            self.assertEqual(j, self.JSON_CONFIG)
        finally:
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
        "path": "/rjarry/libyang-cffi",
        "enabled": false
      },
      {
        "proto": "http",
        "host": "foobar.com",
        "port": 8080,
        "path": "/index.html",
        "enabled": true
      }
    ]
  }
}
'''

    def test_data_parse_state_json(self):
        dnode = self.ctx.parse_data_str(
            self.JSON_STATE, 'json', data=True, no_yanglib=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.dump_str('json', pretty=True)
            self.assertEqual(j, self.JSON_STATE)
        finally:
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
    <enabled>false</enabled>
  </url>
  <url>
    <proto>http</proto>
    <host>foobar.com</host>
    <port>8080</port>
    <path>/index.html</path>
    <enabled>true</enabled>
  </url>
</conf>
'''

    def test_data_parse_config_xml(self):
        dnode = self.ctx.parse_data_str(self.XML_CONFIG, 'xml', config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.dump_str('xml', pretty=True)
            self.assertEqual(xml, self.XML_CONFIG)
        finally:
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
'''

    def test_data_parse_data_xml(self):
        dnode = self.ctx.parse_data_str(
            self.XML_STATE, 'xml', data=True, no_yanglib=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.dump_str('xml', pretty=True)
            self.assertEqual(xml, self.XML_STATE)
        finally:
            dnode.free()

    def test_data_create_paths(self):
        state = self.ctx.create_data_path('/yolo-system:state')
        try:
            state.create_path('hostname', 'foo')
            state.create_path('speed', 1234)
            state.create_path('number', 1000)
            state.create_path('number', 2000)
            state.create_path('number', 3000)
            u = state.create_path('url[proto="https"][host="github.com"]')
            u.create_path('path', '/rjarry/libyang-cffi')
            u.create_path('enabled', False)
            u = state.create_path('url[proto="http"][host="foobar.com"]')
            u.create_path('port', 8080)
            u.create_path('path', '/index.html')
            u.create_path('enabled', True)
            state.validate(strict=True)
            self.assertEqual(state.dump_str('json', pretty=True), self.JSON_STATE)
        finally:
            state.free()

    def test_data_create_invalid_type(self):
        s = self.ctx.create_data_path('/yolo-system:state')
        try:
            with self.assertRaises(LibyangError):
                s.create_path('speed', 1234000000000000000000000000)
        finally:
            s.free()

    def test_data_create_invalid_regexp(self):
        s = self.ctx.create_data_path('/yolo-system:state')
        try:
            with self.assertRaises(LibyangError):
                s.create_path('hostname', 'INVALID.HOST')
        finally:
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
                    'enabled': False,
                },
                {
                    'proto': 'http',
                    'host': 'foobar.com',
                    'port': 8080,
                    'path': '/index.html',
                    'enabled': True,
                },
            ],
        },
    }

    def test_data_to_dict(self):
        dnode = self.ctx.parse_data_str(self.JSON_CONFIG, 'json', config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            dic = dnode_to_dict(dnode)
        finally:
            dnode.free()
        self.assertEqual(dic, self.DICT_CONFIG)

    def test_data_from_dict(self):
        schema = self.ctx.get_module('yolo-system')
        dnode = dict_to_dnode(self.DICT_CONFIG, schema)
        try:
            j = dnode.dump_str('json', pretty=True)
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))
