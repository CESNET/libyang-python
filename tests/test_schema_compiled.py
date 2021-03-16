# Copyright (c) 2020 CESNET, z.s.p.o.
# SPDX-License-Identifier: BSD-3-Clause
# Author David Sedlák <xsedla1d@stud.fit.vutbr.cz>

from unittest.mock import patch, Mock

from _libyang import ffi, lib

from libyang2.schema_compiled import (
    SCModule,
    SCContainer,
    SCList,
    SCRpc,
    SCNotification,
    SCIdentity,
    SCNode,
    SCWhen,
    SCChoice,
    SCCase,
    SCLeaf,
    SCLeafList,
    SCAnydata,
    SCAnyxml,
    SCAction,
    SCExtensionInstance,
    SCExtension,
    SCMust,
    SCInout,
    SCType,
    SCTypeNumeric,
    SCTypeDec64,
    SCTypeString,
    SCPattern,
    SCTypeEnum,
    SCEnumItem,
    SCTypeBits,
    SCBitItem,
    SCTypeLeafref,
    SCTypeIdentityref,
    SCTypeInstanceid,
    SCTypeUnion,
    SCTypeBinary,
    SCRangeSigned,
    SCRangeUnsigned,
)
from libyang2 import Context

from tests.schema_checkers import SCWrappersTestCheckers, SWrapperTestCheckers


class TestSCModule(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCModule type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_module *")
        self.tested_type = SCModule(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("mod", "module")

    def test_rpcs(self):
        """Mock rpcs array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            rpcs_gen = self.tested_type.rpcs()
            self.assertRaises(StopIteration, next, rpcs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.rpcs)

            # test 2 imports in the array
            rpcs = ffi.new("struct lysc_node_action[2]")
            self.tested_ctype.rpcs = rpcs
            str0 = ffi.new("char[]", b"name0")
            self.tested_ctype.rpcs[0].name = str0
            str1 = ffi.new("char[]", b"name1")
            self.tested_ctype.rpcs[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            rpcs_gen = self.tested_type.rpcs()
            first = next(rpcs_gen)
            self.assertTrue(isinstance(first, SCRpc))
            self.assertEqual(first.name, "name0")
            self.assertEqual(next(rpcs_gen).name, "name1")
            self.assertRaises(StopIteration, next, rpcs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.rpcs)

    def test_notifications(self):
        """Mock notifs array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            notifs_gen = self.tested_type.notifications()
            self.assertRaises(StopIteration, next, notifs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.rpcs)

            # test 2 notifications in the array
            notifs = ffi.new("struct lysc_node_notif[2]")
            self.tested_ctype.notifs = notifs
            str0 = ffi.new("char[]", b"name0")
            self.tested_ctype.notifs[0].name = str0
            str1 = ffi.new("char[]", b"name1")
            self.tested_ctype.notifs[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            notifs_gen = self.tested_type.notifications()
            first = next(notifs_gen)
            self.assertTrue(isinstance(first, SCNotification))
            self.assertEqual(first.name, "name0")
            self.assertEqual(next(notifs_gen).name, "name1")
            self.assertRaises(StopIteration, next, notifs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.notifs)

    def test_extension_instances(self):
        self.check_extension_instnaces()


class TestSCIdentity(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCIdentity type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_ident *")
        self.tested_type = SCIdentity(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_module(self):
        self.check_lys_module_member("module", "module")

    def test_derived_identities(self):
        """Mock deviated_by array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            deriveds_gen = self.tested_type.derived_identities()
            self.assertRaises(StopIteration, next, deriveds_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.derived)

            # test 2 notifications in the array
            idents = ffi.new("struct lysc_ident *[2]")
            self.tested_ctype.derived = idents
            id0 = ffi.new("struct lysc_ident *")
            id1 = ffi.new("struct lysc_ident *")
            self.tested_ctype.derived[0] = id0
            self.tested_ctype.derived[1] = id1
            mocked_lib.get_array_size.return_value = 2

            depfs_gen = self.tested_type.derived_identities()
            first = next(depfs_gen)
            self.assertTrue(isinstance(first, SCIdentity))
            self.assertEqual(first._cdata, idents[0])
            self.assertEqual(next(depfs_gen)._cdata, idents[1])
            self.assertRaises(StopIteration, next, depfs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.derived)

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_status(self):
        self.check_status()


class TestSCNode(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCNode type and it's sub-types"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node *")
        self.tested_type = SCNode(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("module", "module")

    def test_parent(self):
        self.check_parent()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_ref(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instnaces()


class TestSCContainer(TestSCNode):
    """Unit tests for SCContainer type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_container *")
        self.tested_type = SCContainer(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_musts()

    def test_actions(self):
        self.check_actions()

    def test_notifications(self):
        self.check_notifications()

    def test_whens(self):
        self.check_whens()


class TestSCCase(TestSCNode):
    """Unit tests for SCCase type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_case *")
        self.tested_type = SCCase(self.tested_ctype, self.ctx)

    def test_whens(self):
        self.check_whens()


class TestSCChoice(TestSCNode):
    """Unit tests for SCChoice type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_choice *")
        self.tested_type = SCChoice(self.tested_ctype, self.ctx)

    def test_default(self):
        # empty
        self.assertIsNone(self.tested_type.default)

        # non-empty
        case = ffi.new("struct lysc_node_case *")
        self.tested_ctype.dflt = case
        self.assertTrue(self.tested_type.default)
        self.assertTrue(isinstance(self.tested_type.default, SCCase))

    def test_whens(self):
        self.check_whens()


class TestSCLeaf(TestSCNode):
    """Unit tests for SCLeaf type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_leaf *")
        self.tested_type = SCLeaf(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_musts()

    def test_type(self):
        self.check_type()

    def test_units(self):
        self.check_char_pointer_getter("units", "units")

    def test_whens(self):
        self.check_whens()


class TestSCLeafList(TestSCLeaf):
    """Unit tests for SCLeafList type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_leaflist *")
        self.tested_type = SCLeafList(self.tested_ctype, self.ctx)

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()

    def test_config(self):
        self.check_config()


class TestSCList(TestSCNode):
    """Unit tests for SCList type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_list *")
        self.tested_type = SCList(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_musts()

    def test_actions(self):
        self.check_actions()

    def test_notifications(self):
        self.check_notifications()

    def test_min(self):
        self.check_min()

    def test_max(self):
        self.check_max()

    def test_whens(self):
        self.check_whens()


class TestSCAnydata(TestSCNode):
    """Unit tests for SCList type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_anydata *")
        self.tested_type = SCAnydata(self.tested_ctype, self.ctx)

    def test_musts(self):
        self.check_musts()

    def test_whens(self):
        self.check_whens()


class TestSCAnyxml(TestSCAnydata):
    """Unit tests for SCAnyxml type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_anydata *")
        self.tested_type = SCAnyxml(self.tested_ctype, self.ctx)


class TestSCAction(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCAction type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_action *")
        self.tested_type = SCAction(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("module", "module")

    def test_parent(self):
        self.check_parent()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_status(self):
        self.check_status()


class TestRpc(TestSCAction):
    """Unit tests for SCRpc type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_action *")
        self.tested_type = SCRpc(self.tested_ctype, self.ctx)


class TestSCNotification(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCNotification type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_notif *")
        self.tested_type = SCNotification(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("module", "module")

    def test_parent(self):
        self.check_parent()

    def test_status(self):
        self.check_status()

    def test_musts(self):
        self.check_musts()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instnaces()


class TestSCExtensionInstance(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCNotification type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_ext_instance *")
        self.tested_type = SCExtensionInstance(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_module(self):
        self.check_lys_module_member("module", "module")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_argument(self):
        self.check_char_pointer_getter("argument", "argument")

    def test_definition(self):
        # empty
        self.assertIsNone(self.tested_type.definition)

        # non-empty
        definition = ffi.new("struct lysc_ext *")
        setattr(self.tested_ctype, "def", definition)
        self.assertTrue(isinstance(self.tested_type.definition, SCExtension))
        self.assertEqual(self.tested_type.definition._cdata, definition)


class TestSCWhen(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCWhen type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_when *")
        self.tested_type = SCWhen(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_status(self):
        self.check_status()


class TestSCMust(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCMust type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_must *")
        self.tested_type = SCMust(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_emsg(self):
        self.check_char_pointer_getter("emsg", "error_message")

    def test_eapptag(self):
        self.check_char_pointer_getter("eapptag", "error_app_tag")

    def test_extension_instances(self):
        self.check_extension_instnaces()


class TestSCInout(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCInout type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_node_action_inout *")
        self.tested_type = SCInout(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_musts(self):
        self.check_musts()


class TestSCExtension(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCExtension type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_ext *")
        self.tested_type = SCExtension(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_argument(self):
        self.check_char_pointer_getter("argument", "argument")

    def test_extension(self):
        self.check_extension_instnaces()

    def test_module(self):
        self.check_lys_module_member("module", "module")


class TestSCType(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCType type and it's subtypes"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type *")
        self.tested_type = SCType(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_extension_instances(self):
        self.check_extension_instnaces()


class TestSCTypeNumeric(TestSCType):
    """Unit tests for SCTypeNumeric type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_num *")
        self.tested_type = SCTypeNumeric(self.tested_ctype, self.ctx)

    def test_range(self):
        self.check_range()


class TestSCTypeDec64(TestSCTypeNumeric):
    """Unit tests for TypeDec64 type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_dec *")
        self.tested_type = SCTypeDec64(self.tested_ctype, self.ctx)

    def fraction_digits(self):
        self.tested_ctype.fraction_digits = 11
        self.assertEqual(self.tested_type.fraction_digits, 11)


class TestSCTypeString(TestSCType):
    """Unit tests for SCTypeString type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_str *")
        self.tested_type = SCTypeString(self.tested_ctype, self.ctx)

    def test_length(self):
        self.check_length()

    def test_patterns(self):
        """Mock patterns array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            patterns_gen = self.tested_type.patterns()
            self.assertRaises(StopIteration, next, patterns_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.patterns
            )

            # test 2 patterns in the array
            patterns = ffi.new("struct lysc_pattern *[2]")
            pattern0 = ffi.new("struct lysc_pattern *")
            pattern1 = ffi.new("struct lysc_pattern *")
            patterns[0] = pattern0
            patterns[1] = pattern1
            expr0 = ffi.new("char[]", b"\x15pattern0")
            expr1 = ffi.new("char[]", b"\x06pattern1")
            patterns[0].expr = expr0
            patterns[1].expr = expr1
            self.tested_ctype.patterns = patterns
            mocked_lib.get_array_size.return_value = 2

            patterns_gen = self.tested_type.patterns()
            first = next(patterns_gen)
            self.assertTrue(isinstance(first, SCPattern))
            self.assertEqual(first.regexp, ("pattern0", True))
            self.assertEqual(next(patterns_gen).regexp, ("pattern1", False))
            self.assertRaises(StopIteration, next, patterns_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.patterns)


class TestSCTypeEnum(TestSCType):
    """Unit tests for SCTypeString type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_enum *")
        self.tested_type = SCTypeEnum(self.tested_ctype, self.ctx)

    def test_enums(self):
        """Mock enums array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            enums_gen = self.tested_type.enums()
            self.assertRaises(StopIteration, next, enums_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.enums)

            # test 2 enums in the array
            enumerations = ffi.new("struct lysc_type_bitenum_item [2]")
            name0 = ffi.new("char[]", b"name0")
            name1 = ffi.new("char[]", b"name1")
            enumerations[0].name = name0
            enumerations[1].name = name1
            self.tested_ctype.enums = enumerations
            mocked_lib.get_array_size.return_value = 2

            enums_gen = self.tested_type.enums()
            first = next(enums_gen)
            self.assertTrue(isinstance(first, SCEnumItem))
            self.assertEqual(first.name, "name0")
            self.assertEqual(next(enums_gen).name, "name1")
            self.assertRaises(StopIteration, next, enums_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.enums)

    def test_default(self):
        self.check_char_pointer_getter("dflt", "default")


class TestSCTypeEnum(TestSCType):
    """Unit tests for SCTypeString type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_bits *")
        self.tested_type = SCTypeBits(self.tested_ctype, self.ctx)

    def test_enums(self):
        """Mock enums array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            bits_gen = self.tested_type.bits()
            self.assertRaises(StopIteration, next, bits_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.bits)

            # test 2 enums in the array
            bits = ffi.new("struct lysc_type_bitenum_item [2]")
            name0 = ffi.new("char[]", b"name0")
            name1 = ffi.new("char[]", b"name1")
            bits[0].name = name0
            bits[1].name = name1
            self.tested_ctype.bits = bits
            mocked_lib.get_array_size.return_value = 2

            bits_gen = self.tested_type.bits()
            first = next(bits_gen)
            self.assertTrue(isinstance(first, SCBitItem))
            self.assertEqual(first.name, "name0")
            self.assertEqual(next(bits_gen).name, "name1")
            self.assertRaises(StopIteration, next, bits_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.bits)


class TestSCTypeLeafref(TestSCType):
    """Unit tests for SCTypeLeafref type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_leafref *")
        self.tested_type = SCTypeLeafref(self.tested_ctype, self.ctx)

    def test_realtype(self):
        # empty
        self.assertIsNone(self.tested_type.realtype)

        # non_empty
        realtype = ffi.new("struct lysc_type *")
        self.tested_ctype.realtype = realtype
        self.tested_ctype.basetype = lib.LY_TYPE_BITS
        self.assertEqual(self.tested_type.realtype._cdata, realtype)

    def test_require_instance(self):
        self.check_require_instance()


class TestSCTypeIdentityref(TestSCType):
    """Unit tests for SCTypeIdentityref type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_identityref *")
        self.tested_type = SCTypeIdentityref(self.tested_ctype, self.ctx)

    def test_bases(self):
        """Mock bases array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            bases_gen = self.tested_type.bases()
            self.assertRaises(StopIteration, next, bases_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.bases)

            # test 2 notifications in the array
            bases = ffi.new("struct lysc_ident *[2]")
            ident0 = ffi.new("struct lysc_ident *")
            ident1 = ffi.new("struct lysc_ident *")
            bases[0] = ident0
            bases[1] = ident1
            self.tested_ctype.bases = bases
            mocked_lib.get_array_size.return_value = 2

            bases_gen = self.tested_type.bases()
            first = next(bases_gen)
            self.assertTrue(isinstance(first, SCIdentity))
            self.assertEqual(first._cdata, bases[0])
            self.assertEqual(next(bases_gen)._cdata, bases[1])
            self.assertRaises(StopIteration, next, bases_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.bases)


class TestSCTypeInstanceid(TestSCType):
    """Unit tests for SCTypeInstanceid type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_instanceid *")
        self.tested_type = SCTypeInstanceid(self.tested_ctype, self.ctx)

    def test_require_instance(self):
        self.check_require_instance()


class TestSCTypeUnion(TestSCType):
    """Unit tests for SCTypeUnion type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_union *")
        self.tested_type = SCTypeUnion(self.tested_ctype, self.ctx)

    def test_types(self):
        """Mock types array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            types_gen = self.tested_type.types()
            self.assertRaises(StopIteration, next, types_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.types)

            # test 2 notifications in the array
            types = ffi.new("struct lysc_type *[2]")
            type0 = ffi.new("struct lysc_type *")
            type1 = ffi.new("struct lysc_type *")
            types[0] = type0
            types[1] = type1
            self.tested_ctype.types = types
            mocked_lib.get_array_size.return_value = 2

            types_gen = self.tested_type.types()
            first = next(types_gen)
            self.assertTrue(isinstance(first, SCType))
            self.assertEqual(first._cdata, types[0])
            self.assertEqual(next(types_gen)._cdata, types[1])
            self.assertRaises(StopIteration, next, types_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.types)


class TestSCTypeBinary(TestSCType):
    """Unit tests for SCTypeBinary type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_bin *")
        self.tested_type = SCTypeBinary(self.tested_ctype, self.ctx)

    def test_length(self):
        self.check_length()


class TestSCRangeSigned(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCRangeSigned type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_range *")
        self.tested_type = SCRangeSigned(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_emsg(self):
        self.check_char_pointer_getter("emsg", "error_message")

    def test_eapptag(self):
        self.check_char_pointer_getter("eapptag", "error_app_tag")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_min(self):
        # empty
        self.assertIsNone(self.tested_type.min)

        # non-empty
        parts = ffi.new("struct lysc_range_part *")
        self.tested_ctype.parts = parts
        self.tested_ctype.parts.min_64 = -20
        self.assertEqual(self.tested_type.min, -20)
        self.tested_ctype.parts.min_64 = 999999999
        self.assertEqual(self.tested_type.min, 999999999)

    def test_max(self):
        # empty
        self.assertIsNone(self.tested_type.max)

        # non-empty
        parts = ffi.new("struct lysc_range_part *")
        self.tested_ctype.parts = parts
        self.tested_ctype.parts.max_64 = -20
        self.assertEqual(self.tested_type.max, -20)
        self.tested_ctype.parts.max_64 = 999999999
        self.assertEqual(self.tested_type.max, 999999999)


class TestSCRangeUnsigned(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCRangeSigned type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_range *")
        self.tested_type = SCRangeUnsigned(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_emsg(self):
        self.check_char_pointer_getter("emsg", "error_message")

    def test_eapptag(self):
        self.check_char_pointer_getter("eapptag", "error_app_tag")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_min(self):
        # empty
        self.assertIsNone(self.tested_type.min)

        # non-empty
        parts = ffi.new("struct lysc_range_part *")
        self.tested_ctype.parts = parts
        self.tested_ctype.parts.min_u64 = 11
        self.assertEqual(self.tested_type.min, 11)
        self.tested_ctype.parts.min_u64 = 50
        self.assertEqual(self.tested_type.min, 50)

    def test_max(self):
        # empty
        self.assertIsNone(self.tested_type.max)

        # non-empty
        parts = ffi.new("struct lysc_range_part *")
        self.tested_ctype.parts = parts
        self.tested_ctype.parts.max_u64 = 11
        self.assertEqual(self.tested_type.max, 11)
        self.tested_ctype.parts.max_u64 = 1125899900000000
        self.assertEqual(self.tested_type.max, 1125899900000000)


class TestSCPattern(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCpattern type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_pattern *")
        self.tested_type = SCPattern(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_expr(self):
        regexp = ffi.new("char[]", b"\x15pattern0")
        self.tested_ctype.expr = regexp
        self.assertEqual(self.tested_type.regexp, ("pattern0", True))

        regexp = ffi.new("char[]", b"\x06pattern1")
        self.tested_ctype.expr = regexp
        self.assertEqual(self.tested_type.regexp, ("pattern1", False))

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_emsg(self):
        self.check_char_pointer_getter("emsg", "error_message")

    def test_eapptag(self):
        self.check_char_pointer_getter("eapptag", "error_app_tag")

    def test_extension_instances(self):
        self.check_extension_instnaces()


class TestSCBitItem(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCBitItem type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_bitenum_item *")
        self.tested_type = SCBitItem(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_iffeatures(self):
        self.check_iffeatures()

    def test_position(self):
        # empty
        self.assertIsNone(self.tested_type.position)

        self.tested_ctype.flags |= lib.LYS_SET_VALUE
        self.tested_ctype.position = 20
        self.assertEqual(self.tested_type.position, 20)
        self.tested_ctype.position = 1048576
        self.assertEqual(self.tested_type.position, 1048576)

    def test_status(self):
        self.check_status()


class TestSCBitItem(SCWrappersTestCheckers, SWrapperTestCheckers):
    """Unit tests for SCEnumItem type"""

    def setUp(self):
        self.ctx = Context()
        self.tested_ctype = ffi.new("struct lysc_type_bitenum_item *")
        self.tested_type = SCEnumItem(self.tested_ctype, self.ctx)

    def tearDown(self):
        self.ctx.destroy()

    def test_name(self):
        self.check_char_pointer_getter("name", "name")

    def test_description(self):
        self.check_char_pointer_getter("dsc", "description")

    def test_reference(self):
        self.check_char_pointer_getter("ref", "reference")

    def test_extension_instances(self):
        self.check_extension_instnaces()

    def test_position(self):
        # empty
        self.assertIsNone(self.tested_type.value)

        self.tested_ctype.flags |= lib.LYS_SET_VALUE
        self.tested_ctype.value = 20
        self.assertEqual(self.tested_type.value, 20)
        self.tested_ctype.value = -50
        self.assertEqual(self.tested_type.value, -50)

    def test_status(self):
        self.check_status()
