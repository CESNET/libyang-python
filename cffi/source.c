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

static int
lyd_wd_toprint(const struct lyd_node *node, int options)
{
    const struct lyd_node *subroot, *next, *elem;
    int flag = 0;

    if (options & LYP_WD_TRIM) {
        /* do not print default nodes */
        if (node->dflt) {
            /* implicit default node */
            return 0;
        } else if (node->schema->nodetype & (LYS_LEAF | LYS_LEAFLIST)) {
            if (lyd_wd_default((struct lyd_node_leaf_list *)node)) {
                /* explicit default node */
                return 0;
            }
        } else if ((node->schema->nodetype & (LYS_CONTAINER)) && !((struct lys_node_container *)node->schema)->presence) {
            /* get know if non-presence container contains non-default node */
            for (subroot = node->child; subroot && !flag; subroot = subroot->next) {
                LY_TREE_DFS_BEGIN(subroot, next, elem) {
                    if (elem->dflt) {
                        /* skip subtree */
                        goto trim_dfs_nextsibling;
                    }
                    switch (elem->schema->nodetype) {
                    case LYS_LEAF:
                    case LYS_LEAFLIST:
                        if (!lyd_wd_default((struct lyd_node_leaf_list *)elem)) {
                            /* non-default node */
                            flag = 1;
                        }
                        break;
                    case LYS_ANYDATA:
                    case LYS_ANYXML:
                    case LYS_NOTIF:
                    case LYS_ACTION:
                    case LYS_LIST:
                        /* non-default nodes */
                        flag = 1;
                        break;
                    case LYS_CONTAINER:
                        if (((struct lys_node_container *)elem->schema)->presence) {
                            /* non-default node */
                            flag = 1;
                        }
                        break;
                    default:
                        break;
                    }
                    if (flag) {
                        break;
                    }

                    /* modified LY_TREE_DFS_END */
                    /* select element for the next run - children first */
                    /* child exception for leafs, leaflists and anyxml without children */
                    if (elem->schema->nodetype & (LYS_LEAF | LYS_LEAFLIST | LYS_ANYDATA)) {
                        next = NULL;
                    } else {
                        next = elem->child;
                    }
                    if (!next) {
trim_dfs_nextsibling:
                        /* no children */
                        if (elem == subroot) {
                            /* we are done, (START) has no children */
                            break;
                        }
                        /* try siblings */
                        next = elem->next;
                    }
                    while (!next) {
                        /* parent is already processed, go to its sibling */
                        elem = elem->parent;
                        /* no siblings, go back through parents */
                        if (elem->parent == subroot->parent) {
                            /* we are done, no next element to process */
                            break;
                        }
                        next = elem->next;
                    }
                }
            }
            if (!flag) {
                /* only default nodes in subtree, do not print the container */
                return 0;
            }
        }
    } else if (node->dflt && !(options & LYP_WD_MASK) && !(node->schema->flags & LYS_CONFIG_R)) {
        /* LYP_WD_EXPLICIT
         * - print only if it contains status data in its subtree */
        LY_TREE_DFS_BEGIN(node, next, elem) {
            if (elem->schema->flags & LYS_CONFIG_R) {
                flag = 1;
                break;
            }
            LY_TREE_DFS_END(node, next, elem)
        }
        if (!flag) {
            return 0;
        }
    } else if (node->dflt && node->schema->nodetype == LYS_CONTAINER && !(options & LYP_KEEPEMPTYCONT)) {
        /* avoid empty default containers */
        LY_TREE_DFS_BEGIN(node, next, elem) {
            if (elem->schema->nodetype != LYS_CONTAINER) {
                flag = 1;
                break;
            }
            LY_TREE_DFS_END(node, next, elem)
        }
        if (!flag) {
            return 0;
        }
    }

    return 1;
}

/* This function is not exported in the public symbols of libyang.so.
 * It has been copied here verbatim. */
int
lyd_toprint(const struct lyd_node *node, int options)
{
    struct lys_node *scase, *sparent;
    struct lyd_node *first;

    if (!lyd_wd_toprint(node, options)) {
        /* wd says do not print, but make exception for direct descendants of case nodes without other printable nodes */
        for (sparent = lys_parent(node->schema); sparent && (sparent->nodetype == LYS_USES); sparent = lys_parent(sparent));
        if (!sparent || (sparent->nodetype != LYS_CASE)) {
            /* parent not a case */
            return 0;
        }
        scase = sparent;

        for (sparent = lys_parent(scase); sparent && (sparent->nodetype == LYS_USES); sparent = lys_parent(sparent));
        if (!sparent || (sparent->nodetype != LYS_CHOICE)) {
            /* weird */
            return 0;
        }
        if (((struct lys_node_choice *)sparent)->dflt == scase) {
            /* this is a default case, respect the previous original toprint flag */
            return 0;
        }

        /* try to find a sibling that will be printed */
        for (first = node->prev; first->prev->next; first = first->prev);
        LY_TREE_FOR(first, first) {
            if (first == node) {
                /* skip this node */
                continue;
            }

            /* find schema parent, whether it is the same case */
            for (sparent = lys_parent(first->schema); sparent && (sparent->nodetype == LYS_USES); sparent = lys_parent(sparent));
            if ((sparent == scase) && lyd_wd_toprint(first, options)) {
                /* this other node will be printed, we do not have to print the current one */
                return 0;
            }
        }

        /* there is no case child that will be printed, print this node */
        return 1;
    }

    return 1;
}

static uint8_t lypy_module_implemented(const struct lys_module *module)
{
	if (module)
		return module->implemented;
	return 0;
}
