# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák

import unittest
from unittest.mock import patch, Mock

from _libyang import ffi, lib

from libyang.schema_parsed import (
    SPModule,
    SPImport,
    SPRevision,
    SPSubmodule,
    SPInclude,
    SPExtension,
    SPExtensionInstance,
    SPStatementGeneric,
    SPFeature,
    SPIdentity,
    SPTypedef,
    SPGrouping,
    SPAugment,
    SPAction,
    SPRpc,
    SPInputOutput,
    SPNotification,
    SPDeviation,
    SPDeaviateAdd,
    SPDeviateDelete,
    SPType,
    SPEnum,
    SPBit,
    SPWhen,
    SPRestriction,
    SPDeviate,
    SPDeviateNotSupported,
    SPDeviateReplace,
    SPNode,
    SPList,
    SPLeaf,
    SPContainer,
    SPLeafList,
    SPChoice,
    SPAnyxml,
    SPAnydata,
    SPUses,
    SPRefine,
    SPPattern,
    SPNodeUnknown,
    SPCase,
)
from libyang import Context
from tests.schema_checkers import SPWrappersTestCheckers, SWrapperTestCheckers


class TestSPModule(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPModule type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_module *")
        self.tested_type = SPModule(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("mod", "module")

    def test_revisions(self):
        self.check_revs()

    def test_imports(self):
        self.check_imports()

    def test_includes(self):
        self.check_includes()

    def test_extensions(self):
        self.check_extensions()

    def test_features(self):
        self.check_features()

    def test_identities(self):
        self.check_identities()

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_data(self):
        self.check_node_ll("data")

    def test_augments(self):
        self.check_augments()

    def test_rpcs(self):
        self.check_rpcs()

    def test_notifications(self):
        self.check_notifications()

    def test_deviations(self):
        self.check_deviations()

    def test_exts(self):
        self.check_extension_instances()


class TestSPSubmodule(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPSubmodule type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_submodule *")
        self.tested_type = SPSubmodule(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_revisions(self):
        self.check_revs()

    def test_imports(self):
        self.check_imports()

    def test_includes(self):
        self.check_includes()

    def test_extensions(self):
        self.check_extensions()

    def test_features(self):
        self.check_features()

    def test_identities(self):
        self.check_identities()

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_data(self):
        self.check_node_ll("data")

    def test_augments(self):
        self.check_augments()

    def test_rpcs(self):
        self.check_rpcs()

    def test_notifications(self):
        self.check_notifications()

    def test_deviations(self):
        self.check_deviations()

    def test_extensions(self):
        self.check_extensions()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_filepath(self):
        self.tested_ctype.filepath = ffi.NULL
        self.assertIsNone(self.tested_type.filepath)
        self.tested_ctype.filepath = ffi.new("char[]", b"filepath")
        self.assertEqual(self.tested_type.filepath, "filepath")
        self.tested_ctype.filepath = ffi.new("char[]", b"anotherfilepath")
        self.assertEqual(self.tested_type.filepath, "anotherfilepath")

    def test_prefix(self):
        self.check_char_pointer_getter("prefix", "prefix")

    def test_organization(self):
        self.tested_ctype.org = ffi.NULL
        self.assertIsNone(self.tested_type.organization)
        self.tested_ctype.org = ffi.new("char[]", b"testorg")
        self.assertEqual(self.tested_type.organization, "testorg")
        self.tested_ctype.org = ffi.new("char[]", b"yetanothertestorg")
        self.assertEqual(self.tested_type.organization, "yetanothertestorg")

    def test_contact(self):
        self.tested_ctype.contact = ffi.NULL
        self.assertIsNone(self.tested_type.contact)
        self.tested_ctype.contact = ffi.new("char[]", b"testcontact")
        self.assertEqual(self.tested_type.contact, "testcontact")
        self.tested_ctype.contact = ffi.new("char[]", b"anothertestcontact")
        self.assertEqual(self.tested_type.contact, "anothertestcontact")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_version(self):
        self.check_version()


class TestSPRevision(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPRevision type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_revision *")
        self.tested_type = SPRevision(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_date(self):
        self.assertIsNone(self.tested_type.date)
        self.tested_ctype.date = b"02-02-2020"
        self.assertEqual(self.tested_type.date, "02-02-2020")
        self.tested_ctype.date = b"01-10-2020"
        self.assertEqual(self.tested_type.date, "01-10-2020")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_exts(self):
        self.check_extension_instances()


class TestSPImport(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPImport type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_import *")
        self.tested_type = SPImport(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("module", "module")

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_prefix(self):
        self.check_char_pointer_getter("prefix", "prefix")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_revision(self):
        self.check_rev()


class TestSPInclude(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPInclude type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_include *")
        self.tested_type = SPInclude(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_submodule(self):
        # empty
        self.tested_ctype.submodule = ffi.NULL
        self.assertIsNone(self.tested_type.submodule)

        # non-empty
        submod = ffi.new("struct lysp_submodule *")
        name = ffi.new("char[]", b"submod-name")
        self.tested_ctype.submodule = submod
        self.tested_ctype.submodule.name = name
        submod = self.tested_type.submodule
        self.assertTrue(isinstance(submod, SPSubmodule))
        self.assertTrue(submod)
        self.assertEqual(self.tested_type.submodule.name, "submod-name")

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extensions(self):
        self.check_extension_instances()

    def test_revision(self):
        self.check_rev()


class TestSPExtension(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPExtension type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_ext *")
        self.tested_type = SPExtension(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_status(self):
        self.check_status()


class TestSPExtensionInstance(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPExtensionInstance type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_ext_instance *")
        self.tested_type = SPExtensionInstance(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_argument(self):
        self.check_char_pointer_getter("argument", "argument")

    def test_is_from_yin(self):
        self.tested_ctype.yin = 0
        self.assertFalse(self.tested_type.is_from_yin)

        self.tested_ctype.yin |= lib.LYS_YIN
        self.assertTrue(self.tested_type.is_from_yin)


class TestSPStatementGeneric(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPStatementGeneric type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_stmt *")
        self.tested_type = SPStatementGeneric(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_statement(self):
        # empty
        self.tested_ctype.stmt = ffi.NULL
        self.assertIsNone(self.tested_type.statement)

        # non-empty
        statement = ffi.new("char []", b"test-statement")
        self.tested_ctype.stmt = statement
        self.assertEqual(self.tested_type.statement, "test-statement")

    def test_argument(self):
        # empty
        self.tested_ctype.arg = ffi.NULL
        self.assertIsNone(self.tested_type.argument)

        # non-empty
        argument = ffi.new("char []", b"test-argument")
        self.tested_ctype.arg = argument
        self.assertEqual(self.tested_type.argument, "test-argument")

    def test_possible_yin_attribute(self):
        # flag not set
        self.tested_ctype.flags = 0
        self.assertFalse(self.tested_type.possible_yin_attribute)

        # flag set
        self.tested_ctype.flags |= lib.LYS_YIN_ATTR
        self.assertTrue(self.tested_type.possible_yin_attribute)

    def test_iter(self):
        # no successor
        self.tested_ctype.next = ffi.NULL
        it = iter(self.tested_type)
        self.assertRaises(StopIteration, next, it)

        # two successors
        succ0 = ffi.new("struct lysp_stmt *")
        name0 = ffi.new("char []", b"stmt-name0")
        succ1 = ffi.new("struct lysp_stmt *")
        name1 = ffi.new("char []", b"stmt-name1")
        succ0.stmt = name0
        succ0.next = succ1
        succ1.stmt = name1
        succ1.next = ffi.NULL
        self.tested_ctype.next = succ0

        for statement in self.tested_type:
            self.assertTrue(isinstance(statement, SPStatementGeneric))

        it = iter(self.tested_type)
        self.assertEqual(next(it).statement, "stmt-name0")
        self.assertEqual(next(it).statement, "stmt-name1")


class TestSPFeature(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPFeature type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_feature *")
        self.tested_type = SPFeature(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_status(self):
        self.check_status()


class TestSPIdentity(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPIdentity type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_ident *")
        self.tested_type = SPIdentity(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_bases(self):
        self.check_bases()

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_status(self):
        self.check_status()


class TestSPTypedef(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPTypedef type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_tpdf *")
        self.tested_type = SPTypedef(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_units(self):
        self.check_char_pointer_getter("units", "units")

    def test_default(self):
        self.check_qname("default")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_type(self):
        self.check_type()

    def test_status(self):
        self.check_status()


class TestSPGrouping(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPGrouping type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_grp *")
        self.tested_type = SPGrouping(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_parent(self):
        self.check_lysp_node_getter("parent", "parent")

    def test_status(self):
        self.check_status()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_data(self):
        self.check_node_ll("child")

    def test_actions(self):
        self.check_actions()

    def test_notifications(self):
        self.check_notifications()

    def test_extensions_instnaces(self):
        self.check_extension_instances()


class TestSPAugment(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPAugment type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_augment *")
        self.tested_type = SPAugment(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_parent(self):
        self.check_lysp_node_getter("parent", "parent")

    def test_status(self):
        self.check_status()

    def test_nodeid(self):
        self.check_char_pointer_getter("nodeid", "nodeid")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_actions(self):
        self.check_actions()

    def test_notifications(self):
        self.check_notifications()


class TestSPAction(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPAction type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_action *")
        self.tested_type = SPAction(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_parent(self):
        self.check_lysp_node_getter("parent", "parent")

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_input(self):
        self.check_inout("input", "input")

    def test_output(self):
        self.check_inout("output", "output")

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPRpc(TestSPAction):
    """Unit tests for SPRpc type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_action *")
        self.tested_type = SPRpc(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_status(self):
        self.check_status()


class TestSPInputOutput(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPInputOutput type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_action_inout *")
        self.tested_type = SPInputOutput(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_parent(self):
        self.check_lysp_node_getter("parent", "parent")

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_typedefs(self):
        self.check_typedefs()

    def test_grouping(self):
        self.check_groupings()

    def test_data(self):
        self.check_node_ll("child")

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPNotification(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPNotification type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_notif *")
        self.tested_type = SPNotification(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_parent(self):
        self.check_lysp_node_getter("parent", "parent")

    def test_status(self):
        self.check_status()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_child(self):
        self.check_node_ll("child")

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPDeviation(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPDeviation type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_deviation *")
        self.tested_type = SPDeviation(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_nodeid(self):
        self.check_char_pointer_getter("nodeid", "nodeid")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_deviates(self):
        with patch("libyang.utils.lib") as mocked_lib:
            # test empty array
            devsgen = self.tested_type.deviates()
            self.assertRaises(StopIteration, next, devsgen)

            # 2 deviates in the list
            dev0 = ffi.new("struct lysp_deviate *")
            dev1 = ffi.new("struct lysp_deviate *")
            dev0.mod = lib.LYS_DEV_ADD
            dev1.mod = lib.LYS_DEV_DELETE
            dev0.next = dev1
            self.tested_ctype.deviates = dev0

            devsgen = self.tested_type.deviates()
            first = next(devsgen)
            self.assertTrue(isinstance(first, SPDeaviateAdd))
            self.assertTrue(isinstance(next(devsgen), SPDeviateDelete))
            self.assertRaises(StopIteration, next, devsgen)

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPType(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPType type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_type *")
        self.tested_type = SPType(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_range(self):
        self.check_restr("range", "range")

    def test_length(self):
        self.check_restr("length", "length")

    def test_patterns(self):
        """Mock patterns array and try to access it using tested_type"""

        with patch("libyang.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            restr_gen = self.tested_type.patterns()
            self.assertRaises(StopIteration, next, restr_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.patterns
            )

            # test 2 patterns in the array
            restrs = ffi.new("struct lysp_restr[2]")
            emsg0 = ffi.new("char[]", b"value0")
            emsg1 = ffi.new("char[]", b"value1")
            restrs[0].emsg = emsg0
            restrs[1].emsg = emsg1
            self.tested_ctype.patterns = restrs
            mocked_lib.get_array_size.return_value = 2

            restr_gen = self.tested_type.patterns()
            first = next(restr_gen)
            self.assertTrue(isinstance(first, SPPattern))
            self.assertEqual(first.error_message, "value0")
            self.assertEqual(next(restr_gen).error_message, "value1")
            self.assertRaises(StopIteration, next, restr_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.patterns)

    def test_enums(self):
        with patch("libyang.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            enums_gen = self.tested_type.enums()
            self.assertRaises(StopIteration, next, enums_gen)

            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.enums)

            # test 2 enums in the array
            enums = ffi.new("struct lysp_type_enum[2]")
            name0 = ffi.new("char[]", b"enum0")
            name1 = ffi.new("char[]", b"enum1")
            enums[0].name = name0
            enums[1].name = name1
            self.tested_ctype.enums = enums
            mocked_lib.get_array_size.return_value = 2

            enums_gen = self.tested_type.enums()
            first = next(enums_gen)
            self.assertTrue(isinstance(first, SPEnum))
            self.assertEqual(first.name, "enum0")
            self.assertEqual(next(enums_gen).name, "enum1")
            self.assertRaises(StopIteration, next, enums_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.enums)

    def test_bits(self):
        with patch("libyang.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            bits_gen = self.tested_type.bits()
            self.assertRaises(StopIteration, next, bits_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.bits)

            # test 2 bits in the array
            bits = ffi.new("struct lysp_type_enum[2]")
            name0 = ffi.new("char[]", b"bit0")
            name1 = ffi.new("char[]", b"bit1")
            bits[0].name = name0
            bits[1].name = name1
            self.tested_ctype.bits = bits
            mocked_lib.get_array_size.return_value = 2

            bits_gen = self.tested_type.bits()
            first = next(bits_gen)
            self.assertTrue(isinstance(first, SPBit))
            self.assertEqual(first.name, "bit0")
            self.assertEqual(next(bits_gen).name, "bit1")
            self.assertRaises(StopIteration, next, bits_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.bits)

    def test_bases(self):
        self.check_bases()

    def test_types(self):
        with patch("libyang.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            types_gen = self.tested_type.types()
            self.assertRaises(StopIteration, next, types_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.types)

            # test 2 types in the array
            types = ffi.new("struct lysp_type[2]")
            name0 = ffi.new("char[]", b"name0")
            name1 = ffi.new("char[]", b"name1")
            types[0].name = name0
            types[1].name = name1
            self.tested_ctype.types = types
            mocked_lib.get_array_size.return_value = 2

            types_gen = self.tested_type.types()
            first = next(types_gen)
            self.assertTrue(isinstance(first, SPType))
            self.assertEqual(first.name, "name0")
            self.assertEqual(next(types_gen).name, "name1")
            self.assertRaises(StopIteration, next, types_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.types)

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_fraction_digits(self):
        self.tested_ctype.fraction_digits = 20
        self.assertEqual(self.tested_type.fraction_digits, 20)
        self.tested_ctype.fraction_digits = 5
        self.assertEqual(self.tested_type.fraction_digits, 5)

    def test_require_instance(self):
        # flag not set
        self.assertFalse(self.tested_type.require_instance)

        # flag set
        self.tested_ctype.flags |= lib.LYS_SET_REQINST
        self.assertTrue(self.tested_type.require_instance)


class TestSPWhen(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPWhen type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_when *")
        self.tested_type = SPWhen(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_condition(self):
        self.check_char_pointer_getter("cond", "condition")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPRestriction(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPRestriction type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_restr *")
        self.tested_type = SPRestriction(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_argument(self):
        self.check_qname("argument")

    def test_error_message(self):
        self.check_char_pointer_getter("emsg", "error_message")

    def test_error_app_tag(self):
        self.check_char_pointer_getter("eapptag", "error_app_tag")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPDeviate(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPDeviate type and it's subtypes"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_deviate *")
        self.tested_type = SPDeviate(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_iter(self):
        gen = iter(self.tested_type)
        self.assertRaises(StopIteration, next, gen)

        dev0 = ffi.new("struct lysp_deviate *")
        dev1 = ffi.new("struct lysp_deviate *")
        dev0.mod = lib.LYS_DEV_NOT_SUPPORTED
        dev1.mod = lib.LYS_DEV_ADD
        dev0.next = dev1
        self.tested_ctype.next = dev0
        gen = iter(self.tested_type)
        first = next(gen)
        self.assertTrue(isinstance(first, SPDeviateNotSupported))
        second = next(gen)
        self.assertTrue(isinstance(second, SPDeaviateAdd))
        self.assertRaises(StopIteration, next, gen)


class TestSPDeviateDelete(TestSPDeviate):
    """Unit tests for SPDeviateDelete type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_deviate_del *")
        self.tested_type = SPDeviateDelete(self.tested_ctype, self.ctx)

    def test_units(self):
        self.check_char_pointer_getter("units", "units")

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_unique_specifications(self):
        self.check_uniques()

    def test_defaults(self):
        self.check_defaults()


class TestSPDeviateAdd(TestSPDeviateDelete):
    """Unit tests for SPDeviateAdd type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_deviate_add *")
        self.tested_type = SPDeaviateAdd(self.tested_ctype, self.ctx)

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()

    def test_config(self):
        self.check_config()

    def test_mandatory(self):
        self.check_mandatory()

    def test_status(self):
        self.check_status()


class TestSPDeviateReplace(TestSPDeviate):
    """Unit tests for SPDeviateReplace type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_deviate_rpl *")
        self.tested_type = SPDeviateReplace(self.tested_ctype, self.ctx)

    def test_type(self):
        self.check_type_pointer()

    def test_units(self):
        self.check_char_pointer_getter("units", "units")

    def test_config(self):
        self.check_config()

    def test_status(self):
        self.check_status()

    def test_mandatory(self):
        self.check_mandatory()

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()


class TestSPEnum(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPEnum type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_type_enum *")
        self.tested_type = SPEnum(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_value(self):
        # not set
        self.assertIsNone(self.tested_type.value)

        # value set but flug not set
        self.tested_ctype.value = 10
        self.assertIsNone(self.tested_type.value)

        # both value and flag set
        self.tested_ctype.value = 20
        self.tested_ctype.flags |= lib.LYS_SET_VALUE
        self.assertTrue(self.tested_type.value, 20)


class TestSPBit(TestSPEnum):
    """Unit tests for SPBit type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_type_enum *")
        self.tested_type = SPBit(self.tested_ctype, self.ctx)

    def test_value(self):
        # not set
        self.assertIsNone(self.tested_type.position)

        # value set but flug not set
        self.tested_ctype.value = 10
        self.assertIsNone(self.tested_type.position)

        # both value and flag set
        self.tested_ctype.value = 20
        self.tested_ctype.flags |= lib.LYS_SET_VALUE
        self.assertTrue(self.tested_type.position, 20)


class TestSPNode(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPNode type and it's subtypes"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node *")
        self.tested_type = SPNode(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_parent(self):
        self.check_lysp_node_getter("parent", "parent")

    def test_extension_instances(self):
        self.check_extension_instances()


class TestSPContainer(TestSPNode):
    """Unit tests for SPContainer type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_container *")
        self.tested_type = SPContainer(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_presence(self):
        self.check_char_pointer_getter("presence", "presence")

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_actions(self):
        self.check_actions()

    def test_notifications(self):
        self.check_notifications()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()


class TestSPLeaf(TestSPNode):
    """Unit tests for SPLeaf type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_leaf *")
        self.tested_type = SPLeaf(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_type(self):
        self.check_type()

    def test_units(self):
        self.check_char_pointer_getter("units", "units")

    def test_default(self):
        self.check_qname("default")

    def test_config(self):
        self.check_config()

    def test_status(self):
        self.check_status()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()


class TestSPLeafList(TestSPLeaf):
    """Unit tests for SPLeafList type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_leaflist *")
        self.tested_type = SPLeafList(self.tested_ctype, self.ctx)

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()

    def test_default(self):
        self.check_defaults()


class TestSPList(TestSPNode):
    """Unit tests for SPList type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_list *")
        self.tested_type = SPList(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_key(self):
        self.check_char_pointer_getter("key", "key")

    def test_typedefs(self):
        self.check_typedefs()

    def test_groupings(self):
        self.check_groupings()

    def test_actions(self):
        self.check_actions()

    def test_notifications(self):
        self.check_notifications()

    def test_unique_specifications(self):
        self.check_uniques()

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()

    def test_config(self):
        self.check_config()

    def test_status(self):
        self.check_status()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()


class TestSPChoice(TestSPNode):
    """Unit tests for SPChoice type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_choice *")
        self.tested_type = SPChoice(self.tested_ctype, self.ctx)

    def test_default(self):
        self.check_qname("default")

    def test_config(self):
        self.check_config()

    def test_status(self):
        self.check_status()

    def test_mandatory(self):
        self.check_mandatory()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()


class TestSPAnyxml(TestSPNode):
    """Unit tests for SPAnyxml type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_anydata *")
        self.tested_type = SPAnyxml(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_config(self):
        self.check_config()

    def test_status(self):
        self.check_status()

    def test_mandatory(self):
        self.check_mandatory()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()


class TestSPAnydata(TestSPAnyxml):
    """Unit tests for SPAnydata type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_anydata *")
        self.tested_type = SPAnydata(self.tested_ctype, self.ctx)


class TestSPUses(TestSPNode):
    """Unit tests for SPUses type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_node_uses *")
        self.tested_type = SPUses(self.tested_ctype, self.ctx)

    def test_refines(self):
        with patch("libyang.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            refines_gen = self.tested_type.refines()
            self.assertRaises(StopIteration, next, refines_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.refines)

            # test 2 refines in the array
            refines = ffi.new("struct lysp_refine[2]")
            des0 = ffi.new("char[]", b"description0")
            des1 = ffi.new("char[]", b"description1")
            refines[0].dsc = des0
            refines[1].dsc = des1
            self.tested_ctype.refines = refines
            mocked_lib.get_array_size.return_value = 2

            refines_gen = self.tested_type.refines()
            first = next(refines_gen)
            self.assertTrue(isinstance(first, SPRefine))
            self.assertEqual(first.description, "description0")
            self.assertEqual(next(refines_gen).description, "description1")
            self.assertRaises(StopIteration, next, refines_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.refines)

    def test_augments(self):
        self.check_augments()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_when(self):
        self.check_when()

    def test_iffeatures(self):
        self.check_iffeatures()


class TestSPRefine(SPWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SPRefine type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysp_refine *")
        self.tested_type = SPRefine(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_nodeid(self):
        self.check_char_pointer_getter("nodeid", "nodeid")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_musts(self):
        self.check_restrs("musts", "musts")

    def test_presence(self):
        self.check_char_pointer_getter("presence", "presence")

    def test_defaults(self):
        self.check_defaults()

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()

    def test_extension_instances(self):
        self.check_extension_instances()

    def test_config(self):
        self.check_config()

    def test_mandatory(self):
        self.check_mandatory()


class TestSPNodeFactory(unittest.TestCase):
    def setUp(self):
        self.ctx = Context()
        self.node = ffi.new("struct lysp_node *")

    def test_unknown(self):
        self.node.nodetype = lib.LYS_UNKNOWN
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPNodeUnknown))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node *")

    def test_container(self):
        self.node.nodetype = lib.LYS_CONTAINER
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPContainer))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_container *")

    def test_choice(self):
        self.node.nodetype = lib.LYS_CHOICE
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPChoice))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_choice *")

    def test_choice(self):
        self.node.nodetype = lib.LYS_LEAF
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPLeaf))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_leaf *")

    def test_leaf(self):
        self.node.nodetype = lib.LYS_LEAF
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPLeaf))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_leaf *")

    def test_leaflist(self):
        self.node.nodetype = lib.LYS_LEAFLIST
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPLeafList))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_leaflist *")

    def test_list(self):
        self.node.nodetype = lib.LYS_LIST
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPList))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_list *")

    def test_anyxml(self):
        self.node.nodetype = lib.LYS_ANYXML
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPAnyxml))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_anydata *")

    def test_anydata(self):
        self.node.nodetype = lib.LYS_ANYDATA
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPAnydata))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_anydata *")

    def test_rpc(self):
        self.node.nodetype = lib.LYS_RPC
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPRpc))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_action *")

    def test_action(self):
        self.node.nodetype = lib.LYS_ACTION
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPAction))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_action *")

    def test_action(self):
        self.node.nodetype = lib.LYS_NOTIF
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPNotification))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_notif *")

    def test_case(self):
        self.node.nodetype = lib.LYS_CASE
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPCase))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_case *")

    def test_case(self):
        self.node.nodetype = lib.LYS_USES
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPUses))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_uses *")

    def test_input(self):
        self.node.nodetype = lib.LYS_INPUT
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPInputOutput))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_action_inout *")

    def test_output(self):
        self.node.nodetype = lib.LYS_OUTPUT
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPInputOutput))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_action_inout *")

    def test_grouping(self):
        self.node.nodetype = lib.LYS_GROUPING
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPGrouping))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_grp *")

    def test_augment(self):
        self.node.nodetype = lib.LYS_AUGMENT
        nd = SPNode.create_node(self.node, self.ctx)
        self.assertTrue(isinstance(nd, SPAugment))
        self.assertEqual(ffi.typeof(nd._cdata).cname, "struct lysp_node_augment *")
