# -*- coding: utf-8 eval: (blacken-mode 1) -*-
# SPDX-License-Identifier: MIT
#
# July 7 2025, Christian Hopps <chopps@labn.net>
#
# Copyright (c) 2025, LabN Consulting, L.L.C.
#
import logging
import os
import sys
import unittest

from libyang import Context, LibyangError, configure_logging, temp_log_options


YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")


class LogTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(YANG_DIR)
        configure_logging(False, logging.INFO)

    def tearDown(self):
        if self.ctx is not None:
            self.ctx.destroy()
        self.ctx = None

    def _cause_log(self):
        try:
            assert self.ctx is not None
            _ = self.ctx.parse_data_mem("bad", fmt="xml")
        except LibyangError:
            pass

    @unittest.skipIf(sys.version_info < (3, 10), "Test requires Python 3.10+")
    def test_configure_logging(self):
        """Test configure_logging API."""
        with self.assertNoLogs("libyang", level="ERROR"):
            self._cause_log()

        configure_logging(True, logging.INFO)
        with self.assertLogs("libyang", level="ERROR"):
            self._cause_log()

    @unittest.skipIf(sys.version_info < (3, 10), "Test requires Python 3.10+")
    def test_with_temp_log(self):
        """Test configure_logging API."""
        configure_logging(True, logging.INFO)

        with self.assertLogs("libyang", level="ERROR"):
            self._cause_log()

        with self.assertNoLogs("libyang", level="ERROR"):
            with temp_log_options(0):
                self._cause_log()

        with self.assertLogs("libyang", level="ERROR"):
            self._cause_log()
