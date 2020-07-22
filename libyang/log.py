# Copyright (c) 2018-2019 Robin Jarry
# Copyright (c) 2020 6WIND S.A.
# SPDX-License-Identifier: MIT

import logging

from _libyang import ffi, lib
from .util import c2str


# -------------------------------------------------------------------------------------
LOG = logging.getLogger("libyang")
LOG.addHandler(logging.NullHandler())
LOG_LEVELS = {
    lib.LY_LLERR: logging.ERROR,
    lib.LY_LLWRN: logging.WARNING,
    lib.LY_LLVRB: logging.INFO,
    lib.LY_LLDBG: logging.DEBUG,
}


@ffi.def_extern(name="lypy_log_cb")
def libyang_c_logging_callback(level, msg, path):
    args = [c2str(msg)]
    if path:
        fmt = "%s: %s"
        args.append(c2str(path))
    else:
        fmt = "%s"
    LOG.log(LOG_LEVELS.get(level, logging.NOTSET), fmt, *args)


def configure_logging(enable_py_logger: bool, level: int = logging.ERROR) -> None:
    """
    Configure libyang logging behaviour.

    :arg enable_py_logger:
        If False, configure libyang to store the errors in the context until they are
        consumed when Context.error() is called. This is the default behaviour.

        If True, libyang log messages will be sent to the python "libyang" logger and
        will be processed according to the python logging configuration. Note that by
        default, the "libyang" python logger is created with a NullHandler() which means
        that all messages are lost until another handler is configured for that logger.
    :arg level:
        Python logging level. By default only ERROR messages are stored/logged.
    """
    for ly_lvl, py_lvl in LOG_LEVELS.items():
        if py_lvl == level:
            lib.ly_verb(ly_lvl)
            break
    if enable_py_logger:
        lib.ly_log_options(lib.LY_LOLOG | lib.LY_LOSTORE)
        lib.ly_set_log_clb(lib.lypy_log_cb, True)
    else:
        lib.ly_log_options(lib.LY_LOSTORE)
        lib.ly_set_log_clb(ffi.NULL, False)


configure_logging(False, logging.ERROR)
