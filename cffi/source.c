/*
 * Copyright (c) 2018-2022 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>
#include <libyang/version.h>

#if LY_VERSION_MAJOR * 10000 + LY_VERSION_MINOR * 100 + LY_VERSION_MICRO < 40100
#error "This version of libyang bindings only works with libyang soversion 4.1.0+"
#endif
