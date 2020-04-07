# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import os  # isort:skip

# Important: the following *must* remain *before* the import of _libyang
HERE = os.path.dirname(__file__)
LIBDIR = os.path.join(HERE, '_lib')
INCLUDEDIR = os.path.join(HERE, '_include')
if os.path.isdir(LIBDIR):
    os.environ.setdefault(
        'LIBYANG_EXTENSIONS_PLUGINS_DIR', os.path.join(LIBDIR, 'extensions'))
    os.environ.setdefault(
        'LIBYANG_USER_TYPES_PLUGINS_DIR', os.path.join(LIBDIR, 'user_types'))

import logging

from _libyang import ffi
from _libyang import lib

from .data import DNode
from .data import PathOpt
from .schema import Module
from .schema import SNode
from .util import LibyangError
from .util import c2str
from .util import str2c


#------------------------------------------------------------------------------
class Context(object):

    def __init__(self, search_path=None,
                 options=lib.LY_CTX_DISABLE_SEARCHDIR_CWD,
                 pointer=None):
        if pointer is not None:
            self._ctx = ffi.cast('struct ly_ctx *', pointer)
            return  # already initialized

        self._ctx = ffi.gc(lib.ly_ctx_new(ffi.NULL, options),
                           lambda c: lib.ly_ctx_destroy(c, ffi.NULL))
        if not self._ctx:
            raise self.error('cannot create context')

        search_dirs = []
        if 'YANGPATH' in os.environ:
            search_dirs.extend(
                os.environ['YANGPATH'].strip(': \t\r\n\'"').split(':'))
        elif 'YANG_MODPATH' in os.environ:
            search_dirs.extend(
                os.environ['YANG_MODPATH'].strip(': \t\r\n\'"').split(':'))
        if search_path:
            search_dirs.extend(search_path.strip(': \t\r\n\'"').split(':'))

        for path in search_dirs:
            if not os.path.isdir(path):
                continue
            if lib.ly_ctx_set_searchdir(self._ctx, str2c(path)) != 0:
                raise self.error('cannot set search dir')

    def error(self, msg, *args):
        errors = []
        try:
            err = lib.ly_err_first(self._ctx)
            while err:
                e = []
                if err.path:
                    e.append(c2str(err.path))
                if err.msg:
                    e.append(c2str(err.msg))
                if err.apptag:
                    e.append(c2str(err.apptag))
                if e:
                    errors.append(': '.join(e))
                err = err.next
        finally:
            lib.ly_err_clean(self._ctx, ffi.NULL)

        msg %= args
        if errors:
            msg += ': ' + ' '.join(errors)

        return LibyangError(msg)

    def load_module(self, name):
        mod = lib.ly_ctx_load_module(self._ctx, str2c(name), ffi.NULL)
        if not mod:
            raise self.error('cannot load module')

        return Module(self, mod)

    def get_module(self, name):
        mod = lib.ly_ctx_get_module(self._ctx, str2c(name), ffi.NULL, False)
        if not mod:
            raise self.error('cannot get module')

        return Module(self, mod)

    def find_path(self, path):
        node_set = lib.ly_ctx_find_path(self._ctx, str2c(path))
        if not node_set:
            raise self.error('cannot find path')
        try:
            for i in range(node_set.number):
                yield SNode.new(self, node_set.set.s[i])
        finally:
            lib.ly_set_free(node_set)

    def create_data_path(self, path, parent=None, value=None, flags=0):
        lib.lypy_set_errno(0)
        if value is not None:
            if isinstance(value, bool):
                value = str(value).lower()
            elif not isinstance(value, str):
                value = str(value)
        dnode = lib.lyd_new_path(
            parent._node if parent else ffi.NULL,
            self._ctx, str2c(path), str2c(value), 0,
            PathOpt.UPDATE | PathOpt.NOPARENTRET | flags)
        if lib.lypy_get_errno() != 0:
            raise self.error('cannot create data path: %s', path)

        if not dnode and parent:
            # This can happen when path points to an already created leaf and
            # its value does not change.
            # In that case, lookup the existing leaf and return it.
            node_set = lib.lyd_find_path(parent._node, str2c(path))
            try:
                if not node_set or not node_set.number:
                    raise self.error('cannot find path')
                dnode = node_set.set.s[0]
            finally:
                lib.ly_set_free(node_set)

        if not dnode:
            raise self.error('cannot find created path')

        return DNode.new(self, dnode)

    def parse_data_str(self, s, fmt, flags=0):
        dnode = lib.lyd_parse_mem(self._ctx, str2c(s), fmt, flags)
        if not dnode:
            raise self.error('failed to parse data tree')
        return DNode.new(self, dnode)

    def parse_data_file(self, fileobj, fmt, flags=0):
        dnode = lib.lyd_parse_fd(self._ctx, fileobj.fileno(), fmt, flags)
        if not dnode:
            raise self.error('failed to parse data tree')
        return DNode.new(self, dnode)

    def __iter__(self):
        """
        Return an iterator that yields all implemented modules from the context
        """
        idx = ffi.new('uint32_t *')
        mod = lib.ly_ctx_get_module_iter(self._ctx, idx)
        while mod:
            yield Module(self, mod)
            mod = lib.ly_ctx_get_module_iter(self._ctx, idx)


#------------------------------------------------------------------------------
LOG_LEVELS = {
    lib.LY_LLERR: logging.ERROR,
    lib.LY_LLWRN: logging.WARNING,
    lib.LY_LLVRB: logging.INFO,
    lib.LY_LLDBG: logging.DEBUG,
}


@ffi.def_extern(name='lypy_log_cb')
def libyang_c_logging_callback(level, msg, path):
    args = [c2str(msg)]
    if path:
        fmt = '%s: %s'
        args.append(c2str(path))
    else:
        fmt = '%s'
    LOG.log(LOG_LEVELS.get(level, logging.NOTSET), fmt, *args)


def set_log_level(level):
    for ly_lvl, py_lvl in LOG_LEVELS.items():
        if py_lvl == level:
            lib.ly_verb(ly_lvl)
            return


set_log_level(logging.ERROR)
lib.ly_set_log_clb(lib.lypy_log_cb, True)
lib.ly_log_options(lib.LY_LOLOG | lib.LY_LOSTORE)
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())


#------------------------------------------------------------------------------
def lib_dirs():
    dirs = []
    if os.path.isdir(LIBDIR):
        dirs.append(LIBDIR)
    return dirs


#------------------------------------------------------------------------------
def include_dirs():
    dirs = []
    if os.path.isdir(INCLUDEDIR):
        dirs.append(INCLUDEDIR)
    return dirs
