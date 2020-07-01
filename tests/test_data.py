# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import json
import os
import unittest
from unittest.mock import patch

from libyang import Context
from libyang import LibyangError
from libyang import lib
from libyang.data import DContainer
from libyang.data import DRpc


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
    ]
  }
}
'''

    def test_data_parse_config_json(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, 'json', config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem('json', pretty=True)
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
    ]
  }
}
'''

    def test_data_parse_state_json(self):
        dnode = self.ctx.parse_data_mem(
            self.JSON_STATE, 'json', data=True, no_yanglib=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem('json', pretty=True)
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
</conf>
'''

    def test_data_parse_config_xml(self):
        dnode = self.ctx.parse_data_mem(self.XML_CONFIG, 'xml', config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.print_mem('xml', pretty=True)
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
'''

    def test_data_parse_data_xml(self):
        dnode = self.ctx.parse_data_mem(
            self.XML_STATE, 'xml', data=True, no_yanglib=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            xml = dnode.print_mem('xml', pretty=True)
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
            u.create_path('path', '/CESNET/libyang-python')
            u.create_path('enabled', False)
            u = state.create_path('url[proto="http"][host="foobar.com"]')
            u.create_path('port', 8080)
            u.create_path('path', '/index.html')
            u.create_path('enabled', True)
            self.assertEqual(state.print_mem('json', pretty=True), self.JSON_STATE)
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
                    'enabled': False,
                    'path': '/CESNET/libyang-python',
                    'host': 'github.com',
                    'proto': 'https',
                },
                {
                    'port': 8080,
                    'proto': 'http',
                    'path': '/index.html',
                    'enabled': True,
                    'host': 'foobar.com',
                },
            ],
        },
    }

    def test_data_to_dict_config(self):
        dnode = self.ctx.parse_data_mem(self.JSON_CONFIG, 'json', config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            dic = dnode.print_dict()
        finally:
            dnode.free()
        self.assertEqual(dic, self.DICT_CONFIG)

    def test_data_to_dict_rpc_input(self):
        dnode = self.ctx.parse_data_mem(
            '{"yolo-system:format-disk": {"disk": "/dev/sda"}}', 'json', rpc=True)
        self.assertIsInstance(dnode, DRpc)
        try:
            dic = dnode.print_dict()
        finally:
            dnode.free()
        self.assertEqual(dic, {'format-disk': {'disk': '/dev/sda'}})

    def test_data_from_dict_module(self):
        module = self.ctx.get_module('yolo-system')
        dnode = module.parse_data_dict(self.DICT_CONFIG, strict=True, config=True)
        self.assertIsInstance(dnode, DContainer)
        try:
            j = dnode.print_mem('json', pretty=True)
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))

    def test_data_from_dict_invalid(self):
        module = self.ctx.get_module('yolo-system')

        created = []
        freed = []

        class FakeLib:

            def __init__(self, orig):
                self.orig = orig

            def lyd_new(self, *args):
                c = self.orig.lyd_new(*args)
                if c:
                    created.append(c)
                return c

            def lyd_new_leaf(self, *args):
                c = self.orig.lyd_new_leaf(*args)
                if c:
                    created.append(c)
                return c

            def lyd_free(self, dnode):
                freed.append(dnode)
                self.orig.lyd_free(dnode)

            def __getattr__(self, name):
                return getattr(self.orig, name)

        fake_lib = FakeLib(lib)

        root = module.parse_data_dict({
            'conf': {
                'hostname': 'foo',
                'speed': 1234,
                'number': [1000, 2000, 3000],
            }
        }, strict=True, config=True)

        invalid_dict = {
            'url': [
                {
                    'host': 'github.com',
                    'proto': 'https',
                    'enabled': False,
                    'path': '/CESNET/libyang-python',
                },
                {
                    'proto': 'http',
                    'path': '/index.html',
                    'enabled': True,
                    'host': 'foobar.com',
                    'port': 'INVALID.PORT',
                },
            ],
        }

        try:
            with patch('libyang.data.lib', fake_lib):
                with self.assertRaises(LibyangError):
                    root.merge_data_dict(invalid_dict, strict=True, config=True)
            self.assertGreater(len(created), 0)
            self.assertGreater(len(freed), 0)
            self.assertEqual(freed, list(reversed(created)))
        finally:
            root.free()

    def test_data_from_dict_container(self):
        dnode = self.ctx.create_data_path('/yolo-system:conf')
        self.assertIsInstance(dnode, DContainer)
        dnode.merge_data_dict(self.DICT_CONFIG['conf'], strict=True, config=True)
        try:
            j = dnode.print_mem('json', pretty=True)
        finally:
            dnode.free()
        self.assertEqual(json.loads(j), json.loads(self.JSON_CONFIG))

    def test_data_from_dict_leaf(self):
        dnode = self.ctx.create_data_path('/yolo-system:state')
        self.assertIsInstance(dnode, DContainer)
        dnode.merge_data_dict({'hostname': 'foo'}, strict=True, data=True, no_yanglib=True)
        try:
            j = dnode.print_mem('json')
        finally:
            dnode.free()
        self.assertEqual(j, '{"yolo-system:state":{"hostname":"foo"}}')

    def test_data_from_dict_rpc(self):
        dnode = self.ctx.create_data_path('/yolo-system:format-disk')
        self.assertIsInstance(dnode, DRpc)
        dnode.merge_data_dict(
            {'duration': 42}, rpcreply=True, strict=True, no_yanglib=True)
        try:
            j = dnode.print_mem('json')
        finally:
            dnode.free()
        self.assertEqual(j, '{"yolo-system:format-disk":{"duration":42}}')
