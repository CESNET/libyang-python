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

static char *lypy_data_path_pattern(const struct lys_node *node)
{
	const struct lys_module *prev_mod, *mod;
	char *xpath = NULL, *keys = NULL;
	struct ly_set *set = NULL;;
	size_t x;

	if (!node)
		goto cleanup;

	set = ly_set_new();
	if (!set)
		goto cleanup;

	while (node) {
		ly_set_add(set, (void *)node, 0);
		do {
			node = lys_parent(node);
		} while (node && !(node->nodetype & (
			LYS_CONTAINER | LYS_LIST | LYS_RPC)));
	}

	xpath = malloc(2048);
	if (!xpath)
		goto cleanup;
	keys = malloc(512);
	if (!keys)
		goto cleanup;

	x = 0;
	xpath[0] = '\0';

	prev_mod = NULL;
	for (int i = set->number - 1; i > -1; --i) {
		size_t k = 0;
		keys[0] = '\0';
		node = set->set.s[i];
		if (node->nodetype == LYS_LIST) {
			const struct lys_node_list *list;
			list = (const struct lys_node_list *)node;
			for (uint8_t j = 0; j < list->keys_size; j++) {
				k += sprintf(keys + k, "[%s='%%s']",
					list->keys[j]->name);
			}
		}

		mod = lys_node_module(node);
		if (mod && mod != prev_mod) {
			prev_mod = mod;
			x += sprintf(xpath + x, "/%s:%s%s",
				mod->name, node->name, keys);
		} else {
			x += sprintf(xpath + x, "/%s%s", node->name, keys);
		}
	}

cleanup:
	ly_set_free(set);
	free(keys);
	return xpath;
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
