/*
 * Copyright (c) 2018-2022 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>
#include <libyang/version.h>

#if (LY_VERSION_MAJOR != 3)
#error "This version of libyang bindings only works with libyang 3.x"
#endif
