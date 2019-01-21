/*
 * Copyright (c) 2018 Robin Jarry
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

struct ly_ctx;

#define LY_CTX_ALLIMPLEMENTED ...
#define LY_CTX_TRUSTED ...
#define LY_CTX_NOYANGLIBRARY ...
#define LY_CTX_DISABLE_SEARCHDIRS ...
#define LY_CTX_DISABLE_SEARCHDIR_CWD ...
#define LY_CTX_PREFER_SEARCHDIRS ...

struct ly_ctx *ly_ctx_new(const char *, int);
int ly_ctx_set_searchdir(struct ly_ctx *, const char *);
void ly_ctx_destroy(struct ly_ctx *, void *);

typedef enum {
	LY_LLERR,
	LY_LLWRN,
	LY_LLVRB,
	LY_LLDBG,
	...
} LY_LOG_LEVEL;

struct ly_err_item {
	char *msg;
	char *path;
	char *apptag;
	struct ly_err_item *next;
	...;
};

#define LY_LOLOG ...
#define LY_LOSTORE ...
#define LY_LOSTORE_LAST ...
int ly_log_options(int);

LY_LOG_LEVEL ly_verb(LY_LOG_LEVEL);
extern "Python" void lypy_log_cb(LY_LOG_LEVEL, const char *, const char *);
void ly_set_log_clb(void (*)(LY_LOG_LEVEL, const char *, const char *), int);
struct ly_err_item *ly_err_first(const struct ly_ctx *);
void ly_err_clean(struct ly_ctx *, struct ly_err_item *);

struct lys_module {
	const char *name;
	const char *prefix;
	const char *dsc;
	uint8_t rev_size;
	struct lys_revision *rev;
	...;
};

#define LY_REV_SIZE 11
struct lys_revision {
	char date[LY_REV_SIZE];
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	const char *dsc;
	const char *ref;
};

int lys_features_enable(const struct lys_module *, const char *);
int lys_features_disable(const struct lys_module *, const char *);
int lys_features_state(const struct lys_module *, const char *);

struct lys_ext {
	const char *name;
	struct lys_module *module;
	...;
};

struct lys_ext_instance {
	struct lys_ext *def;
	const char *arg_value;
	...;
};

typedef enum {
	LY_TYPE_DER,
	LY_TYPE_BINARY,
	LY_TYPE_BITS,
	LY_TYPE_BOOL,
	LY_TYPE_DEC64,
	LY_TYPE_EMPTY,
	LY_TYPE_ENUM,
	LY_TYPE_IDENT,
	LY_TYPE_INST,
	LY_TYPE_LEAFREF,
	LY_TYPE_STRING,
	LY_TYPE_UNION,
	LY_TYPE_INT8,
	LY_TYPE_UINT8,
	LY_TYPE_INT16,
	LY_TYPE_UINT16,
	LY_TYPE_INT32,
	LY_TYPE_UINT32,
	LY_TYPE_INT64,
	LY_TYPE_UINT64,
	LY_TYPE_UNKNOWN,
	...
} LY_DATA_TYPE;

struct lys_type_bit {
	const char *name;
	const char *dsc;
	uint32_t pos;
	...;
};

struct lys_type_info_bits {
	struct lys_type_bit *bit;
	unsigned int count;
};

struct lys_type_enum {
	const char *name;
	const char *dsc;
	...;
};

struct lys_type_info_enums {
	struct lys_type_enum *enm;
	unsigned int count;
};

struct lys_type_info_lref {
	const char *path;
	struct lys_node_leaf* target;
	int8_t req;
};

struct lys_type_info_union {
	struct lys_type *types;
	unsigned int count;
	int has_ptr_type;
};

union lys_type_info {
	struct lys_type_info_bits bits;
	struct lys_type_info_enums enums;
	struct lys_type_info_lref lref;
	struct lys_type_info_union uni;
	...;
};

struct lys_type {
	LY_DATA_TYPE base;
	uint8_t value_flags;
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	struct lys_tpdf *der;
	struct lys_tpdf *parent;
	union lys_type_info info;
	...;
};

struct lys_tpdf {
	const char *name;
	const char *dsc;
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	const char *units;
	struct lys_type type;
	const char *dflt;
	...;
};

typedef enum lys_nodetype {
	LYS_UNKNOWN,
	LYS_CONTAINER,
	LYS_CHOICE,
	LYS_LEAF,
	LYS_LEAFLIST,
	LYS_LIST,
	LYS_ANYXML,
	LYS_CASE,
	LYS_NOTIF,
	LYS_RPC,
	LYS_INPUT,
	LYS_OUTPUT,
	LYS_GROUPING,
	LYS_USES,
	LYS_AUGMENT,
	LYS_ACTION,
	LYS_ANYDATA,
	LYS_EXT,
	...
} LYS_NODE;

#define LYS_CONFIG_W ...
#define LYS_CONFIG_R ...
#define LYS_CONFIG_SET ...
#define LYS_USERORDERED ...
#define LYS_MAND_TRUE ...
#define LYS_STATUS_DEPRC ...
#define LYS_STATUS_OBSLT ...

struct lys_node {
	const char *name;
	const char *dsc;
	uint16_t flags;
	uint8_t ext_size;
	struct lys_ext_instance **ext;
	LYS_NODE nodetype;
	...;
};

struct lys_node_container {
	const char *presence;
	...;
};

struct lys_node_leaf {
	struct lys_type type;
	const char *units;
	const char *dflt;
	...;
};

struct lys_node_leaflist {
	struct lys_type type;
	const char *units;
	uint32_t min;
	uint32_t max;
	uint8_t dflt_size;
	const char **dflt;
	...;
};

struct lys_node_list {
	uint8_t keys_size;
	struct lys_node_leaf **keys;
	uint32_t min;
	uint32_t max;
	...;
};

union ly_set_set {
	struct lys_node **s;
	...;
};

struct ly_set {
	unsigned int size;
	unsigned int number;
	union ly_set_set set;
};

const struct lys_module *ly_ctx_load_module(struct ly_ctx *, const char *, const char *);
const struct lys_module *ly_ctx_get_module_iter(const struct ly_ctx *, uint32_t *);
const struct lys_module *ly_ctx_get_module(const struct ly_ctx *, const char *, const char *, int);
struct ly_set *ly_ctx_find_path(struct ly_ctx *, const char *);
void ly_set_free(struct ly_set *set);
const struct lys_node_list *lys_is_key(const struct lys_node_leaf *, uint8_t *);

#define LYS_GETNEXT_WITHCHOICE ...
#define LYS_GETNEXT_WITHCASE ...
#define LYS_GETNEXT_WITHGROUPING ...
#define LYS_GETNEXT_WITHINOUT ...
#define LYS_GETNEXT_WITHUSES ...
#define LYS_GETNEXT_INTOUSES ...
#define LYS_GETNEXT_INTONPCONT ...
#define LYS_GETNEXT_PARENTUSES ...
#define LYS_GETNEXT_NOSTATECHECK ...

const struct lys_node *lys_getnext(const struct lys_node *, const struct lys_node *, const struct lys_module *, int);
char *lys_data_path(const struct lys_node *);
char *lys_path(const struct lys_node *, int);
struct lys_module *lys_node_module(const struct lys_node *);
struct lys_module *lys_main_module(const struct lys_module *);
struct lys_node *lys_parent(const struct lys_node *);

typedef enum {
	LYS_OUT_UNKNOWN,
	LYS_OUT_YANG,
	LYS_OUT_YIN,
	LYS_OUT_TREE,
	LYS_OUT_INFO,
	LYS_OUT_JSON,
	...
} LYS_OUTFORMAT;

int lys_print_mem(char **, const struct lys_module *, LYS_OUTFORMAT, const char *, int, int);
int lys_print_fd(int, const struct lys_module *, LYS_OUTFORMAT, const char *, int, int);

/* from libc, needed to free allocated strings */
void free(void *);

/* extra functions */
const struct lys_ext_instance *lypy_find_ext(
	const struct lys_ext_instance **, uint8_t,
	const char *, const char *, const char *);
char *lypy_data_path_pattern(const struct lys_node *);
char *lypy_node_fullname(const struct lys_node *);
