/*
 * Copyright (c) 2018-2019 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>

#if (LY_VERSION_MAJOR != 1)
#error "This version of libyang bindings only works with libyang 1.x"
#endif
#if (LY_VERSION_MINOR < 8)
#error "Need at least libyang 1.8"
#endif

static LY_ERR lypy_get_errno(void)
{
	return ly_errno;
}

static void lypy_set_errno(LY_ERR err)
{
	ly_errno = err;
}

static uint8_t lypy_module_implemented(const struct lys_module *module)
{
	if (module)
		return module->implemented;
	return 0;
}
