# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020-2021 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT

from typing import Iterator, Callable, TYPE_CHECKING

from _libyang import ffi, lib

if TYPE_CHECKING:
    pass


class Node:
    UNKNOWN = lib.LYS_UNKNOWN
    CONTAINER = lib.LYS_CONTAINER
    CHOICE = lib.LYS_CHOICE
    LEAF = lib.LYS_LEAF
    LEAFLIST = lib.LYS_LEAFLIST
    LIST = lib.LYS_LIST
    ANYXML = lib.LYS_ANYXML
    ANYDATA = lib.LYS_ANYDATA

    RPC = lib.LYS_RPC
    ACTION = lib.LYS_ACTION
    NOTIFICATION = lib.LYS_NOTIF

    CASE = lib.LYS_CASE
    USES = lib.LYS_USES
    INPUT = lib.LYS_INPUT
    OUTPUT = lib.LYS_OUTPUT
    GROUPING = lib.LYS_GROUPING
    AUGMENT = lib.LYS_AUGMENT

    KEYWORDS = {
        CONTAINER: "container",
        CHOICE: "choice",
        LEAF: "leaf",
        LEAFLIST: "leaf-list",
        LIST: "list",
        ANYXML: "any-xml",
        ANYDATA: "any-data",
        RPC: "rpc",
        ACTION: "action",
        NOTIFICATION: "notification",
        CASE: "case",
        USES: "uses",
        INPUT: "input",
        OUTPUT: "output",
        GROUPING: "grouping",
        AUGMENT: "augment",
    }


class SchemaFactory:
    """Factory method pattern implemented to unify creation of Schema types.

    Creating all schema wrappers through one method allows higher control
    over the individual instances.
    """

    def __init__(self, context):
        self.referenced = {}
        self.context = context

    wrappers = {}

    def wrap(self, cdata, name: str = None) -> any:
        """Wrap provided cdata with corresponding wrapper type.

        :param cdata: cffi cdata object to wrap
        :param name: optional name of wrapper to use, should be preferably
            used only when desired wrapper type can't be derived from
            cdata ctype. When name is not provided wrapper type registered
            to cdata's ctype is used
        :type name: str
        :returns: Initialized wrapper object saved in curent context
        :rtype: any
        """

        # do not wrap empty values
        if cdata == ffi.NULL:
            return None

        # when name is not provided it's automatically
        # derived from ctype of cdata instance
        if not name:
            # extract type information note that only one level
            # of indirection is supported (there is no difference
            # in . and -> operators on python level)
            cffi_type = ffi.typeof(cdata)
            try:
                item_info = cffi_type.item
                name = item_info.cname
            except AttributeError:
                name = cffi_type.cname
        # deal with strings
        if name == "char":
            return c2str(cdata)
        try:
            wrapper = self.wrappers[name]
        except KeyError:
            raise TypeError(
                "Unknown cdata or name '%r' provided (no"
                " associated wrapper was registered)" % name
            )

        # check if wrapper for given cdata already exists
        wrapped = self.referenced.get(cdata)
        if wrapped:
            return wrapped
        else:
            # if it doesn't exist try to create new wrapper and save
            # reference to wrapped type into self.referenced dictionary
            wrapped = wrapper(cdata, self.context)
            self.referenced[cdata] = wrapped
            return wrapped

    def arr2gen(self, cdata_arr, name: str = None) -> Iterator["WrapperBase"]:
        """Create generator of wrapped elements from sized-array.

        :param cdata_arr: cdata pointer to libyang.so sized array
        :param name: name of alternative wrapper to use when desired wrapper
            can't be derived from cdata's ctype
        :type name: str
        :returns: Generator of initialized wrapper object saved in current context
        :rtype: libyang.utils.WrapperBase
        """

        for i in range(lib.get_array_size(cdata_arr)):
            yield self.wrap(cdata_arr[i], name)

    def ll2gen(
        self, cdata_first, chainer: str = "next", name: str = None
    ) -> Iterator["WrapperBase"]:
        """Create generator of wrapped types from sized-array.

        :param cdata_first: cdata pointer to first element of linked list (ll)
        :param chainer: name of member that connects individual element's in ll
        :type chainer: str
        :param name: name of alternative wrapper to use when desired wrapper
            can't be derived from cdata's ctype
        :type name: str
        :returns: Generator of initialized wrapper object saved in current context
        :rtype: libyang.utils.WrapperBase
        """

        iterator = cdata_first
        while iterator:
            yield self.wrap(iterator, name)
            iterator = getattr(iterator, chainer)

    @classmethod
    def register_type_factory(cls, ctype: str):
        """Decorator to register wrappers that directly
        correspond to types/structs from C.

        :param ctype: name of C struct/type
        :type ctype: str
        """

        if ctype in cls.wrappers:
            raise ValueError("factory for %r type already defined" % ctype)

        def _decor(wrapper: Callable) -> Callable:
            cls.wrappers[ctype] = wrapper
            return wrapper

        return _decor

    @classmethod
    def register_named_type_factory(cls, name: str):
        """Decorator to register wrappers that do not
        directly correspond to types/struct from C but
        are distinguished by name parameter

        :param name: custom name for given wrapper
        :type name: str
        """

        if name in cls.wrappers:
            raise ValueError("factory with %r name is already defined" % name)

        def _decor(wrapper: Callable) -> Callable:
            cls.wrappers[name] = wrapper
            return wrapper

        return _decor

    @classmethod
    def register_subtyped_type_factory(cls, method: str, name: str):
        """Decorator to register wrappers that have
        additional logic associated with their creation
        and hence are created by special class method
        and not just by instantiating one class

        :param method: name of creation method
        :type method: str
        :param name: name of given type
        :type name:
        """

        if name in cls.wrappers:
            raise ValueError("factory with %r name is already defined" % name)

        def _decor(master_type: Callable) -> Callable:
            cls.wrappers[name] = getattr(master_type, method)
            return master_type

        return _decor


def str2c(s, encode=True):
    """Convert python string to cdata char array"""

    if s is None:
        return ffi.NULL
    if hasattr(s, "encode"):
        s = s.encode("utf-8")
    return ffi.new("char []", s)


def c2str(c, decode=True):
    """Convert cdata char array to python string"""

    if c == ffi.NULL:
        return None
    s = ffi.string(c)
    if hasattr(s, "decode"):
        s = s.decode("utf-8")
    return s


class WrapperBase:
    """Base class for all schema wrappers.

    provides default __init__, __repr__, __str__ and _invalidate"""

    def __init__(self, cdata, context):
        """Default constructor for schema types

        :param cdata: cdata object of 'struct lysp*/lysc*/lyd*' type
        :param context: libyang python context instance
        :type context: Context
        """

        self._cdata = cdata
        self._context = context
        self._cdata_valid = True

    def _invalidate(self):
        self._cdata_valid = False

    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    @property
    def context(self) -> "Context":
        return self._context
