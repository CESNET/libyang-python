/*
 * Copyright (c) 2018-2022 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>
#include <libyang/version.h>

#if (LY_VERSION_MAJOR != 2)
#error "This version of libyang bindings only works with libyang 2.x"
#endif
#if (LY_VERSION_MINOR < 25)
#error "Need at least libyang 2.25"
#endif
