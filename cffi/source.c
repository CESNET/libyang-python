/*
 * Copyright (c) 2018-2022 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>
#include <libyang/plugins.h>
#include <libyang/version.h>

#if LY_VERSION_MAJOR * 10000 + LY_VERSION_MINOR * 100 + LY_VERSION_MICRO < 50505
#error "This version of libyang bindings only works with libyang soversion 5.5.5+"
#endif
