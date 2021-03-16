# Copyright (c) 2020 CESNET, z.s.p.o.
# SPDX-License-Identifier: MIT
# Author David Sedlák
#

import logging


from .context import Context
from .log import configure_logging

# imports to initialize registering decorators
from . import schema_parsed
from . import schema_compiled
from . import schema


configure_logging(True, logging.CRITICAL)
