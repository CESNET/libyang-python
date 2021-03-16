# Copyright (c) 2020 CESNET, z.s.p.o.
# SPDX-License-Identifier: BSD-3-Clause
# Author David Sedlák

from typing import TYPE_CHECKING, Union, TextIO

from _libyang import lib, ffi

from .data import data_validation_options
from .utils import c2str, str2c, SchemaFactory, WrapperBase
from .log import LibyangError

if TYPE_CHECKING:
    from .schema_parsed import SPModule
    from .schema_compiled import SCModule
    from .data import DNode


def schema_in_format(fmt_string: str) -> int:
    """Convert schema input format string into libyang2 LYS_IN_* enum"""

    if fmt_string == "yang":
        return lib.LYS_IN_YANG
    if fmt_string == "yin":
        return lib.LYS_IN_YIN
    raise ValueError("unknown schema input format: %r" % fmt_string)


def schema_out_format(fmt_string: str) -> int:
    """Convert schema input format string into libyang2 LYS_IN_* enum"""

    if fmt_string == "yang":
        return lib.LYS_OUT_YANG
    if fmt_string == "yang-compiled":
        return lib.LYS_OUT_YANG_COMPILED
    if fmt_string == "yin":
        return lib.LYS_OUT_YIN
    if fmt_string == "tree":
        return lib.LYS_OUT_TREE
    raise ValueError("unknown schema output format: %r" % fmt_string)


def schema_print_options(print_no_substmt: bool = False, print_shrink=False):
    options = 0

    if print_no_substmt:
        options |= lib.LYS_OUTPUT_NO_SUBSTMT
    if print_shrink:
        options != lib.LYS_PRINT_SHRINK

    return options


def ored_options(
    intonpcont: bool = False,
    nochoice: bool = False,
    output: bool = False,
    withcase: bool = False,
    withchoice: bool = False,
):

    options = 0

    if intonpcont:
        options |= lib.LYS_GETNEXT_INTONPCONT
    if nochoice:
        options |= lib.LYS_GETNEXT_NOCHOICE
    if output:
        options |= lib.LYS_GETNEXT_OUTPUT
    if withcase:
        options |= lib.LYS_GETNEXT_WITHCASE
    if withchoice:
        options |= lib.LYS_GETNEXT_WITHCHOICE

    return options


class SWrapperHasName(WrapperBase):
    """Mixin for wrappers with name member.

    Provides name getter and enhanced __repr__ and __str__ methods.
    """

    @property
    def name(self) -> Union[str, None]:
        """Schema statement's name

        :returns: name of schema statement
        :rtype: str
        """

        return c2str(self._cdata.name)

    def __str__(self) -> str:
        return "<%r: %r>" % (type(self).__name__, self.name)


class SWrapperHasDesRef(WrapperBase):
    """Mixin for wrappers over cdata with description and reference members.

    Provides description and reference getters.
    """

    @property
    def description(self) -> Union[str, None]:
        """Schema statement's description

        :returns: description of schema statement
        :rtype: str
        """

        return c2str(self._cdata.dsc)

    @property
    def reference(self) -> Union[str, None]:
        """Schema statement's reference

        :returns: reference of schema statement
        :rtype: str
        """

        return c2str(self._cdata.ref)


@SchemaFactory.register_type_factory("struct lys_module")
class SModule(
    SWrapperHasDesRef, SWrapperHasName,
):
    """Class representing schema module"""

    @property
    def parsed(self) -> Union["SPModule", None]:
        """Parsed version of module"""

        return self._context.sf.wrap(self._cdata.parsed)

    @property
    def compiled(self) -> Union["SCModule", None]:
        """Compiled version of module"""

        return self._context.sf.wrap(self._cdata.compiled)

    @property
    def revision(self) -> Union[str, None]:
        """Latest revision of module"""

        return c2str(self._cdata.revision)

    @property
    def namespace(self) -> Union[str, None]:
        """Module's namespace"""

        return c2str(self._cdata.ns)

    @property
    def prefix(self) -> Union[str, None]:
        """Module's prefix"""

        return c2str(self._cdata.prefix)

    @property
    def filepath(self) -> Union[str, None]:
        """Module's filepath"""

        return c2str(self._cdata.filepath)

    @property
    def organization(self) -> Union[str, None]:
        """Module's organization"""

        return c2str(self._cdata.org)

    @property
    def contact(self) -> Union[str, None]:
        """Module's contact"""

        return c2str(self._cdata.contact)

    @property
    def implemented(self) -> bool:
        """Return's True when module is implemented in the Context, False otherwise"""

        return bool(self._cdata.implemented)

    def implement(self, features=[]):
        """Implement module into context"""

        self._context.check_retval(lib.lys_set_implemented(self._cdata), ffi.NULL)

    def feature_enable(self, name: str) -> None:
        """Enable module's feature"""
        # TODO rewrite using lys_set_implemented
        # if force:
        #     self._context.check_retval(lib.lys_feature_enable(self._cdata, str2c(name)))
        # else:
        #     self._context.check_retval(
        #         lib.lys_feature_enable_force(self._cdata, str2c(name))
        #     )
        pass

    def feature_enable_all(self):
        """Enable all module's feature"""

        features = ffi.new("char *[2]")
        all = ffi.new("char[]", b"*")
        features[0] = all
        features[1] = ffi.NULL
        self._context.check_retval(lib.lys_set_implemented(self._cdata, features))

    def feature_disable(self, name: str, force: bool = False):
        """Disable module's feature"""
        # TODO rewrite using lys_set_implemented
        # if force:
        #     self._context.check_retval(
        #         lib.lys_feature_disable_force(self._cdata, str2c(name))
        #     )
        # else:
        #     self._context.check_retval(
        #         lib.lys_feature_disable(self._cdata, str2c(name))
        #     )
        pass

    def feature_disable_all(self):
        """Disable all module's feature"""

        features = ffi.new("char *[1]")
        features[0] = ffi.NULL
        self._context.check_retval(lib.lys_set_implemented(self._cdata, features))

    def feature_value(self, name):
        """Get the current real status of the specified feature in the module.

        If the feature is enabled, but some of its if-features are false, the feature is considered disabled.
        """

        ret = lib.lys_feature_value(self._cdata, str2c(name))
        if ret == lib.LY_SUCCESS:
            return True
        if ret == lib.LY_ENOT:
            return False
        if ret == lib.LY_ENOT:
            raise LibyangError(f"no such feature {name}")

    def print(
        self,
        target: Union[TextIO, None] = None,
        fmt: str = "yang",
        line_length: int = 80,
        no_substmt: bool = False,
    ) -> Union[str, None]:
        """Serialize module"""

        out_format = schema_out_format(fmt)
        print_options = schema_print_options(no_substmt)
        if target:
            fd = target.fileno()
            self.context.check_retval(
                lib.lys_print_fd(fd, self._cdata, out_format, line_length, print_options)
            )
        else:
            tmp = ffi.new("char **")
            self.context.check_retval(
                lib.lys_print_mem(
                    tmp, self._cdata, out_format, print_options
                )
            )
            try:
                return c2str(tmp[0])
            finally:
                lib.free(tmp[0])

    def validate_tree(
        self, tree: "Dnode", no_state: bool = False, present: bool = False
    ) -> "DNode":
        """Validate data tree against module"""

        options = data_validation_options(no_state, present)
        tmp = ffi.new("struct lyd_node **")
        tmp[0] = tree._cdata
        self.context.check_retval(
            lib.lyd_validate_module(tmp, self._cdata, options, ffi.NULL)
        )

        return self.context.sf.wrap(tmp[0])


class SWrapperHasModule(WrapperBase):
    """Mixin for wrappers over cdata with module member

    Provides module getter.
    """

    @property
    def module(self) -> Union["SModule", None]:
        """Module in which statement is defined

        :returns: Module where this instance of schema statement is defined
        :rtype: SModule
        """

        return self._context.sf.wrap(self._cdata.module)


class SWrapperHasStatus(WrapperBase):
    """Mixin for wrappers over cdata with available status flags

    Provides status getter.
    """

    @property
    def status(self) -> Union[str, None]:
        """Statement's status

        :returns: status value, one of [current, deprecated, obsolete]
        :rtype: str
        """
        if self._cdata.flags & lib.LYS_STATUS_CURR:
            return "current"
        elif self._cdata.flags & lib.LYS_STATUS_DEPRC:
            return "deprecated"
        elif self._cdata.flags & lib.LYS_STATUS_OBSLT:
            return "obsolete"
        else:
            return None


class SWrapperHasConfig(WrapperBase):
    """Mixin for wrappers over cdata with available config flags

    Provides config getter.
    """

    @property
    def config(self) -> Union[bool, None]:
        """Statement's config

        :returns: True when statement is part of config, False otherwise.
            None is returned when not defined.
        :rtype: bool
        """

        if self._cdata.flags & lib.LYS_CONFIG_W:
            return True
        elif self._cdata.flags & lib.LYS_CONFIG_R:
            return False
        else:
            return None


class SWrapperHasUnits(WrapperBase):
    """Mixin for wrappers over cdata with units member.

    Provides units getter.
    """

    @property
    def units(self) -> Union[str, None]:
        """Statement's units if present

        :returns: string representing statement's units or None
            when units are not defined
        :rtype: str
        """
        return self._context.sf.wrap(self._cdata.units)


class SWrapperHasEmsgEpptag(WrapperBase):
    """Mixin for wrappers over cdata with emsg and epptag members.

    Provides error_mesage and error_app_tag getters.
    """

    @property
    def error_message(self) -> str:
        """Schema statement's error-message

        :returns: error_message of schema statement
        :rtype: str
        """

        return self._context.sf.wrap(self._cdata.emsg)

    @property
    def error_app_tag(self) -> str:
        """Schema statement' error-app-tag

        :returns: reference of schema statement
        :rtype: str
        """

        return self._context.sf.wrap(self._cdata.eapptag)


class SWrapperHasArgument(WrapperBase):
    """Mixin for wrappers over cdata with argument member.

    Provides argument getter.
    """

    @property
    def argument(self) -> str:
        """Schema statement's argument

        :returns: reference of schema statement
        :rtype: str
        """
        return self._context.sf.wrap(self._cdata.argument)
