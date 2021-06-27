# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT

from typing import Iterator, Set, Iterable, Union, TextIO, TYPE_CHECKING
from collections.abc import MutableSet

from _libyang import ffi, lib

from .utils import str2c, c2str, SchemaFactory, WrapperBase
from .log import LibyangError
from .schema import schema_in_format
from .data import (
    data_format,
    data_parser_options,
    data_validation_options,
    data_path_creation_options,
)

if TYPE_CHECKING:
    from .schema import SModule
    from .data import DNode


class ContextSearchdirsSet(MutableSet, WrapperBase):
    """Class to manipulate searchdirs of libyang2.so context after creation.

    Interface is same as for built in set.
    """

    def __init__(self, cdata, context: "libyang2.Context", data: Set[str] = set()):
        WrapperBase.__init__(self, cdata, context)
        self.update(data)

    def __contains__(self, item: str) -> bool:
        array = lib.ly_ctx_get_searchdirs(self._cdata)
        if not array:
            return False

        i = 0
        while array[i] != ffi.NULL:
            if c2str(array[i]) == item:
                return True
            i += 1
        return False

    def __iter__(self) -> Iterator[str]:
        array = lib.ly_ctx_get_searchdirs(self._cdata)
        i = 0
        while array and array[i] != ffi.NULL:
            yield c2str(array[i])
            i += 1

    def __len__(self) -> int:
        array = lib.ly_ctx_get_searchdirs(self._cdata)
        if not array:
            return 0

        i = 0
        while array[i] != ffi.NULL:
            i += 1
        return i

    def add(self, searchpath: str):
        """Add new searchapth to context's searchpaths"""

        ret = lib.ly_ctx_set_searchdir(self._cdata, str2c(searchpath))
        if ret != lib.LY_EEXIST:
            self.context.check_retval(ret)

    def discard(self, searchpath: str):
        """Remove searchapth from context's searchpaths"""

        array = lib.ly_ctx_get_searchdirs(self._cdata)
        if not array:
            return
        i = 0
        while array[i] != ffi.NULL:
            if c2str(array[i]) == searchpath:
                self.context.check_retval(lib.ly_ctx_unset_searchdir(self._cdata, array[i]))
                return

    def update(self, searchpaths: Iterable[str]):
        """Add searchpaths from iterable"""

        for item in searchpaths:
            self.add(item)

    def __str__(self) -> str:
        array = lib.ly_ctx_get_searchdirs(self._cdata)
        i = 0
        values = []
        while array and array[i] != ffi.NULL:
            values.append("'" + c2str(array[i]) + "'")
            i += 1

        if values:
            return "{" + ", ".join(values) + "}"
        else:
            return f"{type(self).__name__}()"

    __repr__ = __str__


class Context:
    """Class used to manipulate libyang2.so contexts

    The context concept allows users to work in environments with different
    sets of YANG schemas."""

    def __init__(
        self,
        allimplemented: bool = False,
        disable_searchdir_cwd: bool = False,
        disable_searchdirs: bool = False,
        noyanglibrary: bool = False,
        prefer_searchdirs: bool = False,
        searchdirs: Set[str] = set(),
    ):
        """Inits Context class with given options and searchdirs

        By default all options are set to False and searchdirs set is empty
        """

        options = 0

        if allimplemented:
            options |= lib.LY_CTX_ALL_IMPLEMENTED
        if disable_searchdir_cwd:
            options |= lib.LY_CTX_DISABLE_SEARCHDIR_CWD
        if disable_searchdirs:
            options |= lib.LY_CTX_DISABLE_SEARCHDIRS
        if noyanglibrary:
            options |= lib.LY_CTX_NO_YANGLIBRARY
        if prefer_searchdirs:
            options |= lib.LY_CTX_PREFER_SEARCHDIRS

        temp = ffi.new("struct ly_ctx **")
        if lib.ly_ctx_new(b"", options, temp) != lib.LY_SUCCESS:
            raise LibyangError("unable to create Context")
        if not temp:
            raise LibyangError("unable to create Context")

        self._cdata = temp[0]
        self.searchdirs = ContextSearchdirsSet(self._cdata, self, searchdirs)
        self.sf = SchemaFactory(self)

    def __del__(self) -> None:
        self.destroy()

    def __enter__(self) -> "libyang2.Context":
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.destroy()

    @property
    def noyanglibrary(self):
        return bool(lib.ly_ctx_get_options(self._cdata) & lib.LY_CTX_NO_YANGLIBRARY)

    @property
    def allimplemented(self):
        return bool(lib.ly_ctx_get_options(self._cdata) & lib.LY_CTX_ALL_IMPLEMENTED)

    @allimplemented.setter
    def allimplemented(self, value: bool) -> None:
        if bool(value):
            self.check_retval(
                lib.ly_ctx_set_options(self._cdata, lib.LY_CTX_ALL_IMPLEMENTED)
            )
        else:
            self.check_retval(
                lib.ly_ctx_unset_options(self._cdata, lib.LY_CTX_ALL_IMPLEMENTED)
            )

    @property
    def disable_searchdir_cwd(self):
        return bool(
            lib.ly_ctx_get_options(self._cdata) & lib.LY_CTX_DISABLE_SEARCHDIR_CWD
        )

    @disable_searchdir_cwd.setter
    def disable_searchdir_cwd(self, value: bool) -> None:
        if bool(value):
            self.check_retval(
                lib.ly_ctx_set_options(self._cdata, lib.LY_CTX_DISABLE_SEARCHDIR_CWD)
            )
        else:
            self.check_retval(
                lib.ly_ctx_unset_options(self._cdata, lib.LY_CTX_DISABLE_SEARCHDIR_CWD)
            )

    @property
    def disable_searchdirs(self):
        return bool(lib.ly_ctx_get_options(self._cdata) & lib.LY_CTX_DISABLE_SEARCHDIRS)

    @disable_searchdirs.setter
    def disable_searchdirs(self, value: bool) -> None:
        if bool(value):
            self.check_retval(
                lib.ly_ctx_set_options(self._cdata, lib.LY_CTX_DISABLE_SEARCHDIRS)
            )
        else:
            self.check_retval(
                lib.ly_ctx_unset_options(self._cdata, lib.LY_CTX_DISABLE_SEARCHDIRS)
            )

    @property
    def prefer_searchdirs(self):
        return bool(lib.ly_ctx_get_options(self._cdata) & lib.LY_CTX_PREFER_SEARCHDIRS)

    @prefer_searchdirs.setter
    def prefer_searchdirs(self, value: bool) -> None:
        if bool(value):
            self.check_retval(
                lib.ly_ctx_set_options(self._cdata, lib.LY_CTX_PREFER_SEARCHDIRS)
            )
        else:
            self.check_retval(
                lib.ly_ctx_unset_options(self._cdata, lib.LY_CTX_PREFER_SEARCHDIRS)
            )

    def destroy(self):
        """Function to destroy and release all resources used by context.

        Context nor any of it's components (including schema objects)
        shouldn't be used after context is destroyed.
        """

        if self._cdata:
            lib.ly_ctx_destroy(self._cdata, ffi.NULL)
            self._cdata = None
            self.options = None
            self.searchdirs = None

    def get_modules(self) -> Iterator["SModule"]:
        """Yields all modules loaded in the context"""

        if self._cdata is None:
            raise RuntimeError("Context already destroyed.")
        idx = ffi.new("unsigned int *")
        mod = lib.ly_ctx_get_module_iter(self._cdata, idx)
        while mod:
            yield self.sf.wrap(mod)
            mod = lib.ly_ctx_get_module_iter(self._cdata, idx)

    def get_module(
        self, key: str, revision: str, use_namespace: bool = False
    ) -> Union["SModule", None]:
        rev = ffi.NULL
        if revision:
            rev = str2c(revision)

        if use_namespace:
            return self.sf.wrap(lib.ly_ctx_get_module_ns(self._cdata, str2c(key), rev))
        else:
            return self.sf.wrap(lib.ly_ctx_get_module(self._cdata, str2c(key), rev))

    def get_module_implemented(
        self, key: str, use_namespace: bool = False
    ) -> Union["SModule", None]:
        if use_namespace:
            return self.sf.wrap(
                lib.ly_ctx_get_module_implemented_ns(self._cdata, str2c(key))
            )
        else:
            return self.sf.wrap(
                lib.ly_ctx_get_module_implemented(self._cdata, str2c(key))
            )

    def get_module_latest(
        self, key: str, use_namespace: bool = False
    ) -> Union["SModule", None]:
        if use_namespace:
            return self.sf.wrap(
                lib.ly_ctx_get_module_latest_ns(self._cdata, str2c(key))
            )
        else:
            return self.sf.wrap(lib.ly_ctx_get_module_latest(self._cdata, str2c(key)))

    def parse_data(
        self,
        source: Union[TextIO, str],
        fmt: str = "xml",
        validate_no_state: bool = False,
        validate_present: bool = False,
        parse_no_state: bool = False,
        parse_only: bool = False,
        parse_opaq: bool = False,
        parse_strict: bool = False,
        parse_lyb_mod_update: bool = False,
    ) -> "DNode":
        fmt = data_format(fmt)
        validate_options = data_validation_options(validate_no_state, validate_present)
        parser_options = data_parser_options(
            parse_no_state,
            parse_only,
            parse_opaq,
            parse_strict,
            parse_lyb_mod_update,
        )

        try:
            fd = source.fileno()
            tmp = ffi.new("struct lyd_node **")
            self.check_retval(
                lib.lyd_parse_data_fd(
                    self._cdata, fd, fmt, parser_options, validate_options, tmp
                )
            )

        except AttributeError:
            tmp = ffi.new("struct lyd_node **")
            self.check_retval(
                lib.lyd_parse_data_mem(
                    self._cdata,
                    str2c(source),
                    fmt,
                    parser_options,
                    validate_options,
                    tmp,
                )
            )

        if not tmp:
            raise self.error("unable to parse data tree")

        return self.sf.wrap(tmp[0])

    def load_module(self, name: str, revision: str = None) -> Union["SModule", None]:
        """Load module from searchpaths into context"""

        if self._cdata is None:
            raise RuntimeError("Context already destroyed.")
        features = ffi.new("char *[1]")
        wildcard = ffi.new("char[]", b"*")
        features[0] = ffi.NULL
        mod = lib.ly_ctx_load_module(self._cdata, str2c(name), str2c(revision), ffi.NULL)
        if not mod:
            raise LibyangError(self, "Unable to load module.")
        return self.sf.wrap(mod)

    def dnode_new_path(
        self,
        path: str,
        value: str = None,
        opaq: bool = False,
        output: bool = False,
        update: bool = False,
    ) -> Union["Dnone", None]:
        """Create a new node in the data tree based on a path.

        Cannot be used for anyxml/anydata nodes, for those use Context::dnode_new_path_any"""

        options = data_path_creation_options(opaq, output, update)
        temp = ffi.new("struct lyd_node **")

        self.check_retval(
            lib.lyd_new_path(
                ffi.NULL, self._cdata, str2c(path), str2c(value), options, temp
            )
        )

        return self.sf.wrap(temp[0])

    def reset_latest(self):
        if self._cdata is None:
            raise RuntimeError("Context already destroyed.")
        lib.ly_ctx_reset_latests(self._cdata)

    def error(self, msg: str, *args) -> "libyang2.LibyangError":
        """Create new LibyangError with additional error info from context"""

        msg %= args

        if self._cdata:
            err = lib.ly_err_first(self._cdata)
            if err:
                if err.msg:
                    msg += ": %s" % c2str(err.msg)
                if err.path:
                    msg += ": %s" % c2str(err.path)
            lib.ly_err_clean(self._cdata, ffi.NULL)

        return LibyangError(msg)

    def check_retval(self, retval):
        if retval != lib.LY_SUCCESS:
            raise self.error("libyang2 native function returned error")

    def parse_module(
        self, source: Union[TextIO, str], fmt="yang"
    ) -> Union["SModule", None]:
        """Parse module from file

        :param source:
        :type source: Union[TextIO, str]
        :param fmt: format string, either yang or yin
        :type fmt: str
        :returns: parsed module
        :rtype: SModule
        """
        temp = ffi.new("struct lys_module **")
        in_format = schema_in_format(fmt)

        try:
            fd = source.fileno()
            self.check_retval(lib.lys_parse_fd(self._cdata, fd, in_format, temp))
        except AttributeError:
            self.check_retval(
                lib.lys_parse_mem(self._cdata, str2c(source), in_format, temp)
            )

        if not temp:
            raise self.error("unable to parse module.")

        return self.sf.wrap(temp[0])

    __iter__ = get_modules
