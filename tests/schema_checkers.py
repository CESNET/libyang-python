# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák

import unittest
from unittest.mock import patch, Mock

from _libyang import ffi, lib
from libyang2.schema_compiled import (
    SCExtensionInstance,
    SCIffeature,
    SCContainer,
    SCAction,
    SCMust,
    SCNotification,
    SCTypeString,
    SCWhen,
)

from libyang2.schema_parsed import (
    SPRevision,
    SPImport,
    SPInclude,
    SPExtension,
    SPFeature,
    SPIdentity,
    SPTypedef,
    SPGrouping,
    SPContainer,
    SPList,
    SPAugment,
    SPRpc,
    SPNotification,
    SPDeviation,
    SPExtensionInstance,
    SPType,
    SPAction,
    SPWhen,
    SPInputOutput,
    SPRestriction,
    SPQualifiedName,
)
from libyang2.schema import SModule


class SWrapperTestCheckers(unittest.TestCase):
    """Functions for testing of mixins shared between SP and SC types"""

    def check_lys_module_member(self, cmember, pymember):
        """Mock 'lys_module *' ctype member and try to access it"""

        # empty
        setattr(self.tested_ctype, cmember, ffi.NULL)
        self.assertIsNone(getattr(self.tested_type, pymember))

        # non-empty
        lys_mod = ffi.new("struct lys_module *")
        name = ffi.new("char[]", b"module name")
        lys_mod.name = name
        setattr(self.tested_ctype, cmember, lys_mod)

        self.assertTrue(getattr(self.tested_type, pymember))
        self.assertTrue(isinstance(getattr(self.tested_type, pymember), SModule))
        self.assertEqual(getattr(self.tested_type, pymember).name, "module name")

    def check_char_pointer_getter(self, c_member, py_member):
        """Mock 'char *' ctype member and try to access it using tested_type"""

        # empty
        setattr(self.tested_ctype, c_member, ffi.NULL)
        self.assertIsNone(getattr(self.tested_type, py_member))

        # non-empty
        value = ffi.new("char []", b"testing-value")
        setattr(self.tested_ctype, c_member, value)
        self.assertEqual(getattr(self.tested_type, py_member), "testing-value")

    def check_status(self):
        """Mock status member and try to access it using tested_type"""

        # empty
        self.tested_type.flags = 0
        self.assertIsNone(self.tested_type.status)

        # deprecated
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_STATUS_DEPRC
        self.assertEqual(self.tested_type.status, "deprecated")

        # obsolete
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_STATUS_OBSLT
        self.assertEqual(self.tested_type.status, "obsolete")

        # current
        self.tested_ctype.flags |= lib.LYS_STATUS_CURR
        self.assertEqual(self.tested_type.status, "current")


class SPWrappersTestCheckers(unittest.TestCase):
    """Functions for testing of repeating members in SP types

    This class should be subclassed by unit test fixtures for individual
    SP types. Each subclassed test fixture is supposed to create two
    instance variables called tested_type and tested_ctype. Where
    tested_type is one of SchemaParsed types and tested_ctype is
    underlying cdata object corresponding to tested_type.
    For example test fixture for SPImport type should initiate
    'struct lysp_import *' cdata as tested_ctype and SPImport as tested_type.

    Each subclass can create test fixture suited to tested type
    and call appropriate check_* methods to test functionality of individual
    type components on combination of SP* type and underlying cdata object.
    This allows to test each type individually without unwanted duplication
    of testing code.
    """

    def check_revs(self):
        """Mock revisions array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            revs_gen = self.tested_type.revisions()
            self.assertRaises(StopIteration, next, revs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.revs)

            # test 2 revision in the array
            revs = ffi.new("struct lysp_revision[2]")
            self.tested_ctype.revs = revs
            self.tested_ctype.revs[0].date = b"28-05-2020"
            self.tested_ctype.revs[1].date = b"29-05-2020"
            mocked_lib.get_array_size.return_value = 2

            revs_gen = self.tested_type.revisions()
            first = next(revs_gen)
            self.assertTrue(isinstance(first, SPRevision))
            self.assertEqual(first.date, "28-05-2020")
            self.assertEqual(next(revs_gen).date, "29-05-2020")
            self.assertRaises(StopIteration, next, revs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.revs)

    def check_imports(self):
        """Mock imports array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            imps_gen = self.tested_type.imports()
            self.assertRaises(StopIteration, next, imps_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.imports)

            # test 2 imports in the array
            imports = ffi.new("struct lysp_import[2]")
            self.tested_ctype.imports = imports
            str0 = ffi.new("char[]", b"imp1_name")
            self.tested_ctype.imports[0].name = str0
            str1 = ffi.new("char[]", b"name")
            self.tested_ctype.imports[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            imps_gen = self.tested_type.imports()
            first = next(imps_gen)
            self.assertTrue(isinstance(first, SPImport))
            self.assertEqual(first.name, "imp1_name")
            self.assertEqual(next(imps_gen).name, "name")
            self.assertRaises(StopIteration, next, imps_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.imports)

    def check_includes(self):
        """Mock includes array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            incs_gen = self.tested_type.includes()
            self.assertRaises(StopIteration, next, incs_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.includes
            )

            # test 2 includes in the array
            includes = ffi.new("struct lysp_include[2]")
            self.tested_ctype.includes = includes
            str0 = ffi.new("char[]", b"inc1_name")
            self.tested_ctype.includes[0].name = str0
            str1 = ffi.new("char[5]", b"name")
            self.tested_ctype.includes[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            incs_gen = self.tested_type.includes()
            first = next(incs_gen)
            self.assertTrue(isinstance(first, SPInclude))
            self.assertEqual(first.name, "inc1_name")
            self.assertEqual(next(incs_gen).name, "name")
            self.assertRaises(StopIteration, next, incs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.includes)

    def check_extensions(self):
        """Mock extensions array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            exts_gen = self.tested_type.extensions()
            self.assertRaises(StopIteration, next, exts_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.extensions
            )

            # test 2 extensions in the array
            exts = ffi.new("struct lysp_ext[2]")
            self.tested_ctype.extensions = exts
            str0 = ffi.new("char[]", b"ext1_name")
            self.tested_ctype.extensions[0].name = str0
            str1 = ffi.new("char[]", b"name")
            self.tested_ctype.extensions[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            exts_gen = self.tested_type.extensions()
            first = next(exts_gen)
            self.assertTrue(isinstance(first, SPExtension))
            self.assertEqual(first.name, "ext1_name")
            self.assertEqual(next(exts_gen).name, "name")
            self.assertRaises(StopIteration, next, exts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.extensions)

    def check_features(self):
        """Mock features array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            ftrs_gen = self.tested_type.features()
            self.assertRaises(StopIteration, next, ftrs_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.features
            )

            # test 2 extensions in the array
            features = ffi.new("struct lysp_feature[2]")
            self.tested_ctype.features = features
            str0 = ffi.new("char[]", b"feature_name")
            self.tested_ctype.features[0].name = str0
            str1 = ffi.new("char[]", b"name")
            self.tested_ctype.features[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            ftrs_gen = self.tested_type.features()
            first = next(ftrs_gen)
            self.assertTrue(isinstance(first, SPFeature))
            self.assertEqual(first.name, "feature_name")
            self.assertEqual(next(ftrs_gen).name, "name")
            self.assertRaises(StopIteration, next, ftrs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.features)

    def check_identities(self):
        """Mock identities array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            idents_gen = self.tested_type.identities()
            self.assertRaises(StopIteration, next, idents_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.identities
            )

            # test 2 identities in the array
            idents = ffi.new("struct lysp_ident[2]")
            self.tested_ctype.identities = idents
            str0 = ffi.new("char[]", b"ident_name")
            self.tested_ctype.identities[0].name = str0
            str1 = ffi.new("char[]", b"name")
            self.tested_ctype.identities[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            idents_gen = self.tested_type.identities()
            first = next(idents_gen)
            self.assertTrue(isinstance(first, SPIdentity))
            self.assertEqual(first.name, "ident_name")
            self.assertEqual(next(idents_gen).name, "name")
            self.assertRaises(StopIteration, next, idents_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.identities)

    def check_typedefs(self):
        """Mock typedefs array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            typedefs_gen = self.tested_type.typedefs()
            self.assertRaises(StopIteration, next, typedefs_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.typedefs
            )

            # test 2 typedefs in the array
            typedefs = ffi.new("struct lysp_tpdf[2]")
            self.tested_ctype.typedefs = typedefs
            str0 = ffi.new("char[]", b"tpdf1_name")
            self.tested_ctype.typedefs[0].name = str0
            str1 = ffi.new("char[]", b"name")
            self.tested_ctype.typedefs[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            typedefs_gen = self.tested_type.typedefs()
            first = next(typedefs_gen)
            self.assertTrue(isinstance(first, SPTypedef))
            self.assertEqual(first.name, "tpdf1_name")
            self.assertEqual(next(typedefs_gen).name, "name")
            self.assertRaises(StopIteration, next, typedefs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.typedefs)

    def check_qname(self, py_member):
        """Mock lysp_qname ctype member and try to acess it using tested_type"""

        py_attr = getattr(self.tested_type , py_member)
        self.assertTrue(isinstance(py_attr, SPQualifiedName))
        value = ffi.new("char[]", b"test-string")
        py_attr._cdata.str = value
        self.assertEqual(py_attr.name(), "test-string")

    def check_groupings(self):
        """Mock groupings array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            grps_gen = self.tested_type.groupings()
            self.assertRaises(StopIteration, next, grps_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.groupings
            )

            # test 2 typedefs in the array
            groupings = ffi.new("struct lysp_node_grp[2]")
            self.tested_ctype.groupings = groupings
            str0 = ffi.new("char[]", b"grp1_name")
            self.tested_ctype.groupings[0].name = str0
            str1 = ffi.new("char[]", b"name")
            self.tested_ctype.groupings[1].name = str1
            mocked_lib.get_array_size.return_value = 2

            grps_gen = self.tested_type.groupings()
            first = next(grps_gen)
            self.assertTrue(isinstance(first, SPGrouping))
            self.assertEqual(first.name, "grp1_name")
            self.assertEqual(next(grps_gen).name, "name")
            self.assertRaises(StopIteration, next, grps_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.groupings)

    def check_node_ll(self, c_member):
        """Mock data linked list and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty list
            childs_gen = self.tested_type.childs()
            self.assertRaises(StopIteration, next, childs_gen)

            # test 2 nodes in the list
            node1 = ffi.new("struct lysp_node *")
            node1.nodetype = lib.LYS_CONTAINER
            name1 = ffi.new("char[11]", b"node1_name")
            node1.name = name1
            node2 = ffi.new("struct lysp_node *")
            node2.nodetype = lib.LYS_LIST
            name2 = ffi.new("char[5]", b"name")
            node2.name = name2
            node1.next = node2
            node2.next = ffi.NULL
            setattr(self.tested_ctype, c_member, node1)

            childs_gen = self.tested_type.childs()
            first = next(childs_gen)
            self.assertTrue(isinstance(first, SPContainer))
            self.assertEqual(first.name, "node1_name")
            second = next(childs_gen)
            self.assertTrue(isinstance(second, SPList))
            self.assertEqual(second.name, "name")
            self.assertRaises(StopIteration, next, childs_gen)

    def check_augments(self):
        """Mock augments array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            augs_gen = self.tested_type.augments()
            self.assertRaises(StopIteration, next, augs_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.augments
            )

            # test 2 augments in the array
            augments = ffi.new("struct lysp_node_augment[2]")
            self.tested_ctype.augments = augments
            desc0 = ffi.new("char[]", b"grp1_text")
            self.tested_ctype.augments[0].dsc = desc0
            desc1 = ffi.new("char[]", b"text")
            self.tested_ctype.augments[1].dsc = desc1
            mocked_lib.get_array_size.return_value = 2

            augs_gen = self.tested_type.augments()
            first = next(augs_gen)
            self.assertTrue(isinstance(first, SPAugment))
            self.assertEqual(first.description, "grp1_text")
            self.assertEqual(next(augs_gen).description, "text")
            self.assertRaises(StopIteration, next, augs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.augments)

    def check_rpcs(self):
        """Mock rpcs array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            rpcs_gen = self.tested_type.rpcs()
            self.assertRaises(StopIteration, next, rpcs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.rpcs)

            # test 2 augments in the array
            rpcs = ffi.new("struct lysp_node_action[2]")
            self.tested_ctype.rpcs = rpcs
            name0 = ffi.new("char[10]", b"aaaa_name")
            self.tested_ctype.rpcs[0].name = name0
            name1 = ffi.new("char[5]", b"name")
            self.tested_ctype.rpcs[1].name = name1
            mocked_lib.get_array_size.return_value = 2

            rpcs_gen = self.tested_type.rpcs()
            first = next(rpcs_gen)
            self.assertTrue(isinstance(first, SPRpc))
            self.assertEqual(first.name, "aaaa_name")
            self.assertEqual(next(rpcs_gen).name, "name")
            self.assertRaises(StopIteration, next, rpcs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.rpcs)

    def check_notifications(self):
        """Mock notifs array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            notifs_gen = self.tested_type.notifications()
            self.assertRaises(StopIteration, next, notifs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.notifs)

            # test 2 augments in the array
            notifs = ffi.new("struct lysp_node_notif[2]")
            self.tested_ctype.notifs = notifs
            name0 = ffi.new("char[]", b"aaaa_name")
            self.tested_ctype.notifs[0].name = name0
            name1 = ffi.new("char[]", b"name")
            self.tested_ctype.notifs[1].name = name1
            mocked_lib.get_array_size.return_value = 2

            notifs_gen = self.tested_type.notifications()
            first = next(notifs_gen)
            self.assertTrue(isinstance(first, SPNotification))
            self.assertEqual(first.name, "aaaa_name")
            self.assertEqual(next(notifs_gen).name, "name")
            self.assertRaises(StopIteration, next, notifs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.notifs)

    def check_deviations(self):
        """Mock deviations array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            devs_gen = self.tested_type.deviations()
            self.assertRaises(StopIteration, next, devs_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.deviations
            )

            # test 2 deviations in the array
            deviations = ffi.new("struct lysp_deviation[2]")
            self.tested_ctype.deviations = deviations
            name0 = ffi.new("char[]", b"aaaa_text")
            self.tested_ctype.deviations[0].nodeid = name0
            name1 = ffi.new("char[]", b"text")
            self.tested_ctype.deviations[1].nodeid = name1
            mocked_lib.get_array_size.return_value = 2

            devs_gen = self.tested_type.deviations()
            first = next(devs_gen)
            self.assertTrue(isinstance(first, SPDeviation))
            self.assertEqual(first.nodeid, "aaaa_text")
            self.assertEqual(next(devs_gen).nodeid, "text")
            self.assertRaises(StopIteration, next, devs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.deviations)

    def check_extension_instances(self):
        """Mock exts array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            exts_gen = self.tested_type.extension_instances()
            self.assertRaises(StopIteration, next, exts_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.exts)

            # test 2 extension instances in the array
            exts = ffi.new("struct lysp_ext_instance[2]")
            self.tested_ctype.exts = exts
            name0 = ffi.new("char[]", b"testname")
            self.tested_ctype.exts[0].name = name0
            name1 = ffi.new("char[]", b"text")
            self.tested_ctype.exts[1].name = name1
            mocked_lib.get_array_size.return_value = 2
            exts_gen = self.tested_type.extension_instances()
            first = next(exts_gen)
            self.assertTrue(isinstance(first, SPExtensionInstance))
            self.assertEqual(first.name, "testname")
            self.assertEqual(next(exts_gen).name, "text")
            self.assertRaises(StopIteration, next, exts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.exts)

    def check_version(self):
        """Mock version member and try to access it using tested_type"""

        self.tested_ctype.version = lib.LYS_VERSION_UNDEF
        self.assertEqual(self.tested_type.version, "YANG 1.0")
        self.tested_ctype.version = lib.LYS_VERSION_1_1
        self.assertEqual(self.tested_type.version, "YANG 1.1")
        self.tested_ctype.version = lib.LYS_VERSION_1_0
        self.assertEqual(self.tested_type.version, "YANG 1.0")

    def check_rev(self):
        """Mock rev member and try to access it using tested_type"""

        # empty
        self.assertIsNone(self.tested_type.revision)

        # non-empty
        self.tested_ctype.rev = b"28-05-2020"
        self.assertEqual(self.tested_type.revision, "28-05-2020")
        self.tested_ctype.rev = b"31-07-2020"
        self.assertEqual(self.tested_type.revision, "31-07-2020")

    def check_iffeatures(self):
        """Mock iffeatures array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            ifftrs_gen = self.tested_type.iffeatures()
            self.assertRaises(StopIteration, next, ifftrs_gen)
            mocked_lib.get_array_size.assert_called_once_with(
                self.tested_ctype.iffeatures
            )

            # test 2 iffeatures in the array
            iffeatures = ffi.new("struct lysp_qname [2]")
            iff0 = ffi.new("char[]", b"iffeature0")
            iff1 = ffi.new("char[]", b"iffeature1")
            iffeatures[0].str = iff0
            iffeatures[1].str = iff1
            self.tested_ctype.iffeatures = iffeatures
            mocked_lib.get_array_size.return_value = 2

            ifftrs_gen = self.tested_type.iffeatures()
            first = next(ifftrs_gen)
            self.assertTrue(isinstance(first, SPQualifiedName))
            self.assertEqual(first.name(), "iffeature0")
            self.assertEqual(next(ifftrs_gen).name(), "iffeature1")
            self.assertRaises(StopIteration, next, ifftrs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.iffeatures)

    def check_bases(self):
        """Mock bases array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            bases_gen = self.tested_type.bases()
            self.assertRaises(StopIteration, next, bases_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.bases)

            # test 2 iffeatures in the array
            bases = ffi.new("char *[2]")
            base0 = ffi.new("char[]", b"base0")
            base1 = ffi.new("char[]", b"base1")
            bases[0] = base0
            bases[1] = base1
            self.tested_ctype.bases = bases
            mocked_lib.get_array_size.return_value = 2

            bases_gen = self.tested_type.bases()
            first = next(bases_gen)
            self.assertTrue(isinstance(first, str))
            self.assertEqual(first, "base0")
            self.assertEqual(next(bases_gen), "base1")
            self.assertRaises(StopIteration, next, bases_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.bases)

    def check_type(self):
        """Mock type member and try to access it using tested_type"""

        name = ffi.new("char []", b"type-name")
        self.tested_ctype.type.name = name
        self.assertTrue(self.tested_type.type)
        self.assertTrue(isinstance(self.tested_type.type, SPType))
        self.assertEqual(self.tested_type.type.name, "type-name")

    def check_type_pointer(self):
        """Mock type member and try to access it using tested_type"""

        # empty
        self.assertIsNone(self.tested_type.type)

        # non-empty
        type = ffi.new("struct lysp_type *")
        name = ffi.new("char []", b"type-name")
        type.name = name
        self.tested_ctype.type = type
        self.assertTrue(self.tested_type.type)
        self.assertTrue(isinstance(self.tested_type.type, SPType))
        self.assertEqual(self.tested_type.type.name, "type-name")

    def check_lysp_node_getter(self, c_member, py_member):
        """Mock struct lysp_node member and try to access it"""

        # empty
        setattr(self.tested_ctype, c_member, ffi.NULL)
        getattr(self.tested_type, py_member)
        self.assertIsNone(getattr(self.tested_type, py_member))

        # non-empty
        nd = ffi.new("struct lysp_node *")
        name = ffi.new("char []", b"node-name")
        nd.nodetype = lib.LYS_LIST
        nd.name = name
        setattr(self.tested_ctype, c_member, nd)

        self.assertTrue(getattr(self.tested_type, py_member))
        self.assertTrue(isinstance(getattr(self.tested_type, py_member), SPList))
        self.assertEqual(getattr(self.tested_type, py_member).name, "node-name")

    def check_actions(self):
        """Mock actions array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            acts_gen = self.tested_type.actions()
            self.assertRaises(StopIteration, next, acts_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.actions)

            # test 2 actions in the array
            actions = ffi.new("struct lysp_node_action[2]")
            name0 = ffi.new("char[]", b"action0")
            name1 = ffi.new("char[]", b"action1")
            actions[0].name = name0
            actions[1].name = name1
            self.tested_ctype.actions = actions
            mocked_lib.get_array_size.return_value = 2

            acts_gen = self.tested_type.actions()
            first = next(acts_gen)
            self.assertTrue(isinstance(first, SPAction))
            self.assertEqual(first.name, "action0")
            self.assertEqual(next(acts_gen).name, "action1")
            self.assertRaises(StopIteration, next, acts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.actions)

    def check_when(self):
        """Mock when member and try to access it using tested_type"""

        # empty
        self.tested_ctype.when = ffi.NULL
        self.assertIsNone(self.tested_type.when)

        # non-empty
        when = ffi.new("struct lysp_when *")
        cond = ffi.new("char []", b"when-condition")
        when.cond = cond
        self.tested_ctype.when = when
        self.assertTrue(self.tested_type.when)
        self.assertTrue(isinstance(self.tested_type.when, SPWhen))
        self.assertEqual(self.tested_type.when.condition, "when-condition")

    def check_inout(self, c_member, py_member):
        """Mock inout member and try to access it using tested_type"""

        parent = ffi.new("struct lysp_node *")
        parent.nodetype = lib.LYS_LIST
        getattr(self.tested_ctype, c_member).parent = parent
        self.assertTrue(getattr(self.tested_type, py_member))
        self.assertTrue(isinstance(getattr(self.tested_type, py_member), SPInputOutput))
        parent_node = getattr(self.tested_type, py_member).parent
        self.assertTrue(isinstance(parent_node, SPList))

    def check_restrs(self, c_member, py_member):
        """Mock rests array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            restr_gen = getattr(self.tested_type, py_member)()
            self.assertRaises(StopIteration, next, restr_gen)

            mocked_lib.get_array_size.assert_called_once_with(
                getattr(self.tested_ctype, c_member)
            )

            # test 2 restrictions in the array
            restrs = ffi.new("struct lysp_restr[2]")
            emsg0 = ffi.new("char[]", b"restr0")
            emsg1 = ffi.new("char[]", b"restr1")
            restrs[0].emsg = emsg0
            restrs[1].emsg = emsg1
            setattr(self.tested_ctype, c_member, restrs)
            mocked_lib.get_array_size.return_value = 2

            restr_gen = getattr(self.tested_type, py_member)()
            first = next(restr_gen)
            self.assertTrue(isinstance(first, SPRestriction))
            self.assertEqual(first.error_message, "restr0")
            self.assertEqual(next(restr_gen).error_message, "restr1")
            self.assertRaises(StopIteration, next, restr_gen)
            mocked_lib.get_array_size.assert_called_with(
                getattr(self.tested_ctype, c_member)
            )

    def check_restr(self, c_member, py_member):
        # empty
        self.assertIsNone(getattr(self.tested_type, py_member))

        # non-empty
        restr = ffi.new("struct lysp_restr *")
        emsg = ffi.new("char[]", b"restr")
        restr.emsg = emsg
        setattr(self.tested_ctype, c_member, restr)
        restriction = getattr(self.tested_type, py_member)
        self.assertTrue(isinstance(restriction, SPRestriction))
        self.assertEqual(restriction.error_message, "restr")

    def check_uniques(self):
        """Mock uniques array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            uniqs_gen = self.tested_type.unique_specifications()
            self.assertRaises(StopIteration, next, uniqs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.uniques)

            # test 2 uniques in the array
            uniques = ffi.new("struct lysp_qname[2]")
            iff0 = ffi.new("char[]", b"unique0")
            iff1 = ffi.new("char[]", b"unique1")
            uniques[0].str = iff0
            uniques[1].str = iff1
            self.tested_ctype.uniques = uniques
            mocked_lib.get_array_size.return_value = 2

            uniqs_gen = self.tested_type.unique_specifications()
            first = next(uniqs_gen)
            self.assertTrue(isinstance(first, SPQualifiedName))
            self.assertEqual(first.name(), "unique0")
            self.assertEqual(next(uniqs_gen).name(), "unique1")
            self.assertRaises(StopIteration, next, uniqs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.uniques)

    def check_defaults(self):
        """Mock defaults array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            # test empty array
            mocked_lib.get_array_size = Mock()
            mocked_lib.get_array_size.return_value = 0
            dflts_gen = self.tested_type.defaults()
            self.assertRaises(StopIteration, next, dflts_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.dflts)

            # test 2 uniques in the array
            defaults = ffi.new("struct lysp_qname[2]")
            def0 = ffi.new("char[]", b"default0")
            def1 = ffi.new("char[]", b"default1")
            defaults[0].str = def0
            defaults[1].str = def1
            self.tested_ctype.dflts = defaults
            mocked_lib.get_array_size.return_value = 2

            dflts_gen = self.tested_type.defaults()
            first = next(dflts_gen)
            self.assertTrue(isinstance(first, SPQualifiedName))
            self.assertEqual(first.name(), "default0")
            self.assertEqual(next(dflts_gen).name(), "default1")
            self.assertRaises(StopIteration, next, dflts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.dflts)

    def check_min(self):
        """Mock min flag and try to access it using tested_type"""

        # not set
        self.assertIsNone(self.tested_type.min)

        # value set, flag not set
        self.tested_ctype.min = 10
        self.assertIsNone(self.tested_type.min)

        # both value and flag set
        self.tested_ctype.min = 20
        self.tested_ctype.flags |= lib.LYS_SET_MIN
        self.assertEqual(self.tested_type.min, 20)

    def check_max(self):
        """Mock max flag and try to access it using tested_type"""

        # not set
        self.assertIsNone(self.tested_type.max)

        # value set, flag not set
        self.tested_ctype.max = 20
        self.assertIsNone(self.tested_type.max)

        # both value and flag set
        self.tested_ctype.max = 40
        self.tested_ctype.flags |= lib.LYS_SET_MAX
        self.assertEqual(self.tested_type.max, 40)

    def check_config(self):
        """Mock config flag and try to access it using tested_type"""

        # not set
        self.tested_ctype.flags = 0
        self.assertIsNone(self.tested_type.config)

        # set to true
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_CONFIG_W
        self.assertTrue(self.tested_type.config)

        # set to false
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_CONFIG_R
        self.assertFalse(self.tested_type.config)

    def check_mandatory(self):
        """Mock mandatory flag and try to access it using tested_type"""

        # not set
        self.tested_ctype.flags = 0
        self.assertIsNone(self.tested_type.mandatory)

        # set to true
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_MAND_TRUE
        self.assertTrue(self.tested_type.mandatory)

        # set to false
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_MAND_FALSE
        self.assertFalse(self.tested_type.mandatory)


class SCWrappersTestCheckers(unittest.TestCase):
    """Functions for testing of repeating members in SC types

    This class should be subclassed by unit test fixtures for individual
    SC types. Each subclassed test fixture is supposed to create two
    instance variables called tested_type and tested_ctype. Where
    tested_type is one of SchemaParsed types and tested_ctype is
    underlying cdata object corresponding to tested_type.
    For example test fixture for SCImport type should initiate
    'struct lysc_import *' cdata as tested_ctype and SCImport as tested_type.

    Each subclass can create test fixture suited to tested type
    and call appropriate check_* methods to test functionality of individual
    type components on combination of SC* type and underlying cdata object.
    This allows to test each type individually without unwanted duplication
    of testing code.
    """

    def check_extension_instnaces(self):
        """Mock exts array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            exts_gen = self.tested_type.extension_instances()
            self.assertRaises(StopIteration, next, exts_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.exts)

            # test 2 extensions in the array
            exts = ffi.new("struct lysc_ext_instance[2]")
            self.tested_ctype.exts = exts
            mocked_lib.get_array_size.return_value = 2

            exts_gen = self.tested_type.extension_instances()
            first = next(exts_gen)
            self.assertTrue(isinstance(first, SCExtensionInstance))
            self.assertEqual(first._cdata, exts[0])
            self.assertEqual(next(exts_gen)._cdata, exts[1])
            self.assertRaises(StopIteration, next, exts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.exts)

    def check_iffeatures(self):
        """Mock exts array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            iffs_gen = self.tested_type.iffeatures()
            self.assertRaises(StopIteration, next, iffs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.exts)

            # test 2 extensions in the array
            iffeatures = ffi.new("struct lysc_iffeature[2]")
            self.tested_ctype.iffeatures = iffeatures
            mocked_lib.get_array_size.return_value = 2

            iffs_gen = self.tested_type.iffeatures()
            first = next(iffs_gen)
            self.assertTrue(isinstance(first, SCIffeature))
            self.assertEqual(first._cdata, iffeatures[0])
            self.assertEqual(next(iffs_gen)._cdata, iffeatures[1])
            self.assertRaises(StopIteration, next, iffs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.iffeatures)

    def check_actions(self):
        """Mock actions array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            acts_gen = self.tested_type.actions()
            self.assertRaises(StopIteration, next, acts_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.actions)

            # test 2 extensions in the array
            actions = ffi.new("struct lysc_node_action[2]")
            self.tested_ctype.actions = actions
            mocked_lib.get_array_size.return_value = 2

            acts_gen = self.tested_type.actions()
            first = next(acts_gen)
            self.assertTrue(isinstance(first, SCAction))
            self.assertEqual(first._cdata, actions[0])
            self.assertEqual(next(acts_gen)._cdata, actions[1])
            self.assertRaises(StopIteration, next, acts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.actions)

    def check_musts(self):
        """Mock musts array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            musts_gen = self.tested_type.musts()
            self.assertRaises(StopIteration, next, musts_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.musts)

            # test 2 extensions in the array
            musts = ffi.new("struct lysc_must[2]")
            self.tested_ctype.musts = musts
            mocked_lib.get_array_size.return_value = 2

            musts_gen = self.tested_type.musts()
            first = next(musts_gen)
            self.assertTrue(isinstance(first, SCMust))
            self.assertEqual(first._cdata, musts[0])
            self.assertEqual(next(musts_gen)._cdata, musts[1])
            self.assertRaises(StopIteration, next, musts_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.musts)

    def check_notifications(self):
        """Mock notifs array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            notifs_gen = self.tested_type.notifications()
            self.assertRaises(StopIteration, next, notifs_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.notifs)

            # test 2 notifications in the array
            notifs = ffi.new("struct lysc_node_notif[2]")
            self.tested_ctype.notifs = notifs
            mocked_lib.get_array_size.return_value = 2

            notifs_gen = self.tested_type.notifications()
            first = next(notifs_gen)
            self.assertTrue(isinstance(first, SCNotification))
            self.assertEqual(first._cdata, notifs[0])
            self.assertEqual(next(notifs_gen)._cdata, notifs[1])
            self.assertRaises(StopIteration, next, notifs_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.notifs)

    def check_type(self):
        # empty
        self.assertIsNone(self.tested_type.type)

        # non-empty
        tp = ffi.new("struct lysc_type *")
        tp.basetype = lib.LY_TYPE_STRING
        self.tested_ctype.type = tp
        self.assertTrue(self.tested_type.type)
        self.assertTrue(isinstance(self.tested_type.type, SCTypeString))
        self.assertEqual(self.tested_type.type._cdata, tp)

    def check_min(self):
        self.tested_ctype.min = 50
        self.assertEqual(self.tested_type.min, 50)

        self.tested_ctype.min = 20
        self.assertEqual(self.tested_type.min, 20)

    def check_max(self):
        self.tested_ctype.max = 50
        self.assertEqual(self.tested_type.max, 50)

        self.tested_ctype.max = 20
        self.assertEqual(self.tested_type.max, 20)

    def check_config(self):
        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_CONFIG_R
        self.assertFalse(self.tested_type.config)

        self.tested_ctype.flags = 0
        self.tested_ctype.flags |= lib.LYS_CONFIG_W
        self.assertTrue(self.tested_type.config)

    def check_parent(self):
        # empty
        self.assertIsNone(self.tested_type.parent)

        # non-empty
        par = ffi.new("struct lysc_node *")
        par.nodetype = lib.LYS_CONTAINER
        self.tested_ctype.parent = par
        self.assertTrue(isinstance(self.tested_type.parent, SCContainer))

    def check_range(self):
        # empty
        self.assertIsNone(self.tested_type.range)

        # non-empty
        range = ffi.new("struct lysc_range *")
        self.tested_ctype.basetype = lib.LY_TYPE_UINT16
        parts = ffi.new("struct lysc_range_part *")
        range.parts = parts
        range.parts.min_u64 = 10
        range.parts.max_u64 = 20
        self.tested_ctype.range = range
        range = self.tested_type.range
        self.assertTrue(range)
        self.assertEqual(range.min, 10)
        self.assertEqual(range.max, 20)

    def check_length(self):
        # empty
        self.assertIsNone(self.tested_type.length)

        # non-empty
        length = ffi.new("struct lysc_range *")
        self.tested_ctype.basetype = lib.LY_TYPE_UINT16
        parts = ffi.new("struct lysc_range_part *")
        length.parts = parts
        length.parts.min_u64 = 10
        length.parts.max_u64 = 20
        self.tested_ctype.length = length
        length = self.tested_type.length
        self.assertTrue(range)
        self.assertEqual(length.min, 10)
        self.assertEqual(length.max, 20)

    def check_require_instance(self):
        # flag not set
        self.assertFalse(self.tested_type.require_instance)

        # flag set
        self.tested_ctype.require_instance = 1
        self.assertTrue(self.tested_type.require_instance)

    def check_whens(self):
        """Mock when array and try to access it using tested_type"""

        with patch("libyang2.utils.lib") as mocked_lib:
            mocked_lib.get_array_size = Mock()
            # test empty array
            mocked_lib.get_array_size.return_value = 0
            whens_gen = self.tested_type.whens()
            self.assertRaises(StopIteration, next, whens_gen)
            mocked_lib.get_array_size.assert_called_once_with(self.tested_ctype.when)

            # test 2 notifications in the array
            whens = ffi.new("struct lysc_when *[2]")
            when0 = ffi.new("struct lysc_when *")
            when1 = ffi.new("struct lysc_when *")
            whens[0] = when0
            whens[1] = when1
            self.tested_ctype.when = whens
            mocked_lib.get_array_size.return_value = 2

            whens_gen = self.tested_type.whens()
            first = next(whens_gen)
            self.assertTrue(isinstance(first, SCWhen))
            self.assertEqual(first._cdata, whens[0])
            self.assertEqual(next(whens_gen)._cdata, whens[1])
            self.assertRaises(StopIteration, next, whens_gen)
            mocked_lib.get_array_size.assert_called_with(self.tested_ctype.when)
