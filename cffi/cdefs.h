/*
 * Copyright (c) 2018-2019 Robin Jarry
 * SPDX-License-Identifier: MIT
 */
struct ly_ctx;

#define	LY_CTX_ALL_IMPLEMENTED ...
#define LY_CTX_REF_IMPLEMENTED ...
#define LY_CTX_NO_YANGLIBRARY ...
#define	LY_CTX_DISABLE_SEARCHDIRS   ...
#define LY_CTX_DISABLE_SEARCHDIR_CWD ...
#define	LY_CTX_PREFER_SEARCHDIRS ...


typedef enum {
	LY_SUCCESS,
	...
} LY_ERR;

LY_ERR ly_ctx_new(const char *, uint16_t, struct ly_ctx **);
void ly_ctx_destroy(struct ly_ctx *);
int ly_ctx_set_searchdir(struct ly_ctx *, const char *);

typedef enum
{
	LY_TYPE_UNKNOWN = 0,
	LY_TYPE_BINARY,
	LY_TYPE_UINT8,
	LY_TYPE_UINT16,
	LY_TYPE_UINT32,
	LY_TYPE_UINT64,
	LY_TYPE_STRING,
	LY_TYPE_BITS,
	LY_TYPE_BOOL,
	LY_TYPE_DEC64,
	LY_TYPE_EMPTY,
	LY_TYPE_ENUM,
	LY_TYPE_IDENT,
	LY_TYPE_INST,
	LY_TYPE_LEAFREF,
	LY_TYPE_UNION,
	LY_TYPE_INT8,
	LY_TYPE_INT16,
	LY_TYPE_INT32,
	LY_TYPE_INT64
} LY_DATA_TYPE;

typedef enum {
	LY_LLERR,
	LY_LLWRN,
	LY_LLVRB,
	LY_LLDBG,
	...
} LY_LOG_LEVEL;

typedef enum {
    LYVE_SUCCESS,
    ...
} LY_VECODE;

#define LY_LOLOG ...
#define LY_LOSTORE ...
#define LY_LOSTORE_LAST ...
int ly_log_options(int);

LY_LOG_LEVEL ly_log_level(LY_LOG_LEVEL);
extern "Python" void lypy_log_cb(LY_LOG_LEVEL, const char *, const char *);
void ly_set_log_clb(void (*)(LY_LOG_LEVEL, const char *, const char *), int);
struct ly_err_item *ly_err_first(const struct ly_ctx *);
void ly_err_clean(struct ly_ctx *, struct ly_err_item *);
LY_VECODE ly_vecode(const struct ly_ctx *);

#define LYS_UNKNOWN ...
#define LYS_CONTAINER ...
#define LYS_CHOICE ...
#define LYS_LEAF ...
#define LYS_LEAFLIST ...
#define LYS_LIST ...
#define LYS_ANYXML ...
#define LYS_ANYDATA ...
#define LYS_CASE ...
#define LYS_RPC ...
#define LYS_ACTION ...
#define LYS_NOTIF ...
#define LYS_USES ...
#define LYS_INPUT ...
#define LYS_OUTPUT ...
#define LYS_GROUPING ...
#define LYS_AUGMENT ...

struct lys_module* ly_ctx_load_module(struct ly_ctx *, const char *, const char *, const char **);
struct lys_module* ly_ctx_get_module(const struct ly_ctx *, const char *, const char *);
struct lys_module* ly_ctx_get_module_iter(const struct ly_ctx *, uint32_t *);

LY_ERR lys_find_xpath(const struct ly_ctx *, const struct lysc_node *, const char *, uint32_t, struct ly_set **);
void ly_set_free(struct ly_set *, void(*)(void *obj));

struct ly_set {
	uint32_t size;
	uint32_t count;
    union {
        struct lyd_node **dnodes;
        struct lysc_node **snodes;
        void **objs;
    };
};

struct lysc_node {
    uint16_t nodetype;
    uint16_t flags;
    struct lys_module *module;
    struct lysc_node *parent;
    struct lysc_node *next;
    struct lysc_node *prev;
    const char *name;
    const char *dsc;
    const char *ref;
    ...;
};

struct ly_err_item {
    LY_LOG_LEVEL level;
    LY_ERR no;
    LY_VECODE vecode;
    char *msg;
    char *path;
    char *apptag;
    struct ly_err_item *next;
    struct ly_err_item *prev;
    ...;
};

struct lyd_node {
    uint32_t hash;
    uint32_t flags;
    const struct lysc_node *schema;
    struct lyd_node_inner *parent;
    struct lyd_node *next;
    struct lyd_node *prev;
    struct lyd_meta *meta;
    void *priv;
};

LY_ERR lys_set_implemented(struct lys_module *,	const char **);

 #define LYD_NEW_PATH_UPDATE ...
 #define LYD_NEW_PATH_OUTPUT ...
 #define LYD_NEW_PATH_OPAQ   ...
 #define LYD_NEW_PATH_BIN_VALUE ...
 #define LYD_NEW_PATH_CANON_VALUE ...
 LY_ERR lyd_new_path(struct lyd_node *, const struct ly_ctx *, const char *, const char *, uint32_t, struct lyd_node **);
 void lyd_free_all(struct lyd_node *node);
 void lyd_free_tree(struct lyd_node *node);

typedef enum {
    LYD_UNKNOWN = 0,
    LYD_XML,
    LYD_JSON,
    LYD_LYB
} LYD_FORMAT;

#define LYD_PRINT_KEEPEMPTYCONT ...
#define LYD_PRINT_SHRINK   ...
#define LYD_PRINT_WD_ALL ...
#define LYD_PRINT_WD_ALL_TAG ...
#define LYD_PRINT_WD_EXPLICIT ...
#define LYD_PRINT_WD_IMPL_TAG ...
#define LYD_PRINT_WD_MASK ...
#define LYD_PRINT_WITHSIBLINGS ...
#define LYD_PRINT_WD_TRIM ...
LY_ERR lyd_print_mem(char **, const struct lyd_node *, LYD_FORMAT, uint32_t);
LY_ERR lyd_print_tree(struct ly_out *, const struct lyd_node *, LYD_FORMAT, uint32_t);
LY_ERR lyd_print_all(struct ly_out *, const struct lyd_node *, LYD_FORMAT, uint32_t);

#define LYD_PARSE_LYB_MOD_UPDATE ...
#define LYD_PARSE_NO_STATE ...
#define LYD_PARSE_ONLY ...
#define LYD_PARSE_OPAQ ...
#define LYD_PARSE_OPTS_MASK ...
#define LYD_PARSE_ORDERED ...
#define LYD_PARSE_STRICT ...

#define LYD_VALIDATE_NO_STATE ...
#define LYD_VALIDATE_PRESENT ...
#define LYD_VALIDATE_OPTS_MASK ...

LY_ERR lyd_parse_data_mem(const struct ly_ctx *, const char *, LYD_FORMAT, uint32_t, uint32_t, struct lyd_node **);

struct ly_in;
struct ly_out;
typedef uint8_t ly_bool;
void ly_in_free(struct ly_in *, ly_bool);
void ly_out_free(struct ly_out *, void(*)(void *arg), ly_bool);
LY_ERR ly_in_new_memory(const char *, struct ly_in **);
LY_ERR ly_in_new_filepath(const char *, size_t, struct ly_in **);
LY_ERR ly_in_new_fd(int, struct ly_in **);
LY_ERR ly_in_new_file(FILE *, struct ly_in **);
LY_ERR ly_out_new_memory(char **, size_t, struct ly_out **);
LY_ERR ly_out_new_filepath(const char *, struct ly_out **);
LY_ERR ly_out_new_file(FILE *, struct ly_out **);
LY_ERR ly_out_new_fd(int, struct ly_out **);

LY_ERR lyd_parse_data(const struct ly_ctx *, struct lyd_node *, struct ly_in *, LYD_FORMAT, uint32_t, uint32_t, struct lyd_node **);

/* from libc, needed to free allocated strings */
void free(void *);
