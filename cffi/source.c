/*
 * Copyright (c) 2018-2019 Robin Jarry
 * SPDX-License-Identifier: MIT
 */

#include <libyang/libyang.h>

static const struct lys_ext_instance *
lypy_find_ext(const struct lys_ext_instance **ext, uint8_t ext_size,
	const char *name, const char *prefix, const char *arg_value)
{
	const struct lys_ext_instance *inst;
	const struct lys_module *module;
	const struct lys_ext *def;
	uint8_t i;

	if (!ext)
		goto notfound;

	for (i = 0; i < ext_size; i++) {
		inst = ext[i];
		def = inst->def;
		if (name && strcmp(def->name, name) != 0)
			continue;
		if (prefix) {
			module = lys_main_module(def->module);
			if (!module)
				goto notfound;
			if (strcmp(module->name, prefix) != 0)
				continue;
		}
		if (arg_value && inst->arg_value) {
			if (strcmp(arg_value, inst->arg_value) != 0)
				continue;
		}
		return inst;
	}

notfound:
	return NULL;
}

static char *lypy_node_fullname(const struct lys_node *node)
{
	const struct lys_module *module;
	char *fullname = NULL;

	module = lys_node_module(node);
	if (!module)
		return NULL;

	if (asprintf(&fullname, "%s:%s", module->name, node->name) < 0)
		return NULL;

	return fullname;
}

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
