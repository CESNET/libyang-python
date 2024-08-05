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
#define LY_CTX_ENABLE_IMP_FEATURES ...
#define LY_CTX_EXPLICIT_COMPILE ...
#define LY_CTX_REF_IMPLEMENTED ...
#define LY_CTX_SET_PRIV_PARSED ...
#define LY_CTX_LEAFREF_EXTENDED ...
#define LY_CTX_LEAFREF_LINKING ...
#define LY_CTX_BUILTIN_PLUGINS_ONLY ...


typedef enum {
    LY_SUCCESS,
    LY_EMEM,
    LY_ESYS,
    LY_EINVAL,
    LY_EEXIST,
    LY_ENOTFOUND,
    LY_EINT,
    LY_EVALID,
    LY_EDENIED,
    LY_EINCOMPLETE,
    LY_ERECOMPILE,
    LY_ENOT,
    LY_EOTHER,
    LY_EPLUGIN = 128
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
    LY_VALUE_CANON,
    LY_VALUE_SCHEMA,
    LY_VALUE_SCHEMA_RESOLVED,
    LY_VALUE_XML,
    LY_VALUE_JSON,
    LY_VALUE_LYB,
    LY_VALUE_STR_NS
} LY_VALUE_FORMAT;

typedef enum {
	LY_LLERR,
	LY_LLWRN,
	LY_LLVRB,
	LY_LLDBG,
	...
} LY_LOG_LEVEL;

typedef enum {
    LYVE_SUCCESS,
    LYVE_SYNTAX,
    LYVE_SYNTAX_YANG,
    LYVE_SYNTAX_YIN,
    LYVE_REFERENCE,
    LYVE_XPATH,
    LYVE_SEMANTICS,
    LYVE_SYNTAX_XML,
    LYVE_SYNTAX_JSON,
    LYVE_DATA,
    LYVE_OTHER
} LY_VECODE;

enum ly_stmt {
    LY_STMT_NONE = 0,
    LY_STMT_NOTIFICATION,
    LY_STMT_INPUT,
    LY_STMT_OUTPUT,
    LY_STMT_ACTION,
    LY_STMT_RPC,
    LY_STMT_ANYDATA,
    LY_STMT_ANYXML,
    LY_STMT_AUGMENT,
    LY_STMT_CASE,
    LY_STMT_CHOICE,
    LY_STMT_CONTAINER,
    LY_STMT_GROUPING,
    LY_STMT_LEAF,
    LY_STMT_LEAF_LIST,
    LY_STMT_LIST,
    LY_STMT_USES,
    LY_STMT_ARGUMENT,
    LY_STMT_BASE,
    LY_STMT_BELONGS_TO,
    LY_STMT_BIT,
    LY_STMT_CONFIG,
    LY_STMT_CONTACT,
    LY_STMT_DEFAULT,
    LY_STMT_DESCRIPTION,
    LY_STMT_DEVIATE,
    LY_STMT_DEVIATION,
    LY_STMT_ENUM,
    LY_STMT_ERROR_APP_TAG,
    LY_STMT_ERROR_MESSAGE,
    LY_STMT_EXTENSION,
    LY_STMT_EXTENSION_INSTANCE,
    LY_STMT_FEATURE,
    LY_STMT_FRACTION_DIGITS,
    LY_STMT_IDENTITY,
    LY_STMT_IF_FEATURE,
    LY_STMT_IMPORT,
    LY_STMT_INCLUDE,
    LY_STMT_KEY,
    LY_STMT_LENGTH,
    LY_STMT_MANDATORY,
    LY_STMT_MAX_ELEMENTS,
    LY_STMT_MIN_ELEMENTS,
    LY_STMT_MODIFIER,
    LY_STMT_MODULE,
    LY_STMT_MUST,
    LY_STMT_NAMESPACE,
    LY_STMT_ORDERED_BY,
    LY_STMT_ORGANIZATION,
    LY_STMT_PATH,
    LY_STMT_PATTERN,
    LY_STMT_POSITION,
    LY_STMT_PREFIX,
    LY_STMT_PRESENCE,
    LY_STMT_RANGE,
    LY_STMT_REFERENCE,
    LY_STMT_REFINE,
    LY_STMT_REQUIRE_INSTANCE,
    LY_STMT_REVISION,
    LY_STMT_REVISION_DATE,
    LY_STMT_STATUS,
    LY_STMT_SUBMODULE,
    LY_STMT_TYPE,
    LY_STMT_TYPEDEF,
    LY_STMT_UNIQUE,
    LY_STMT_UNITS,
    LY_STMT_VALUE,
    LY_STMT_WHEN,
    LY_STMT_YANG_VERSION,
    LY_STMT_YIN_ELEMENT,
    LY_STMT_SYNTAX_SEMICOLON,
    LY_STMT_SYNTAX_LEFT_BRACE,
    LY_STMT_SYNTAX_RIGHT_BRACE,
    LY_STMT_ARG_TEXT,
    LY_STMT_ARG_VALUE
};

#define LY_STMT_NODE_MASK ...

#define LY_LOLOG ...
#define LY_LOSTORE ...
#define LY_LOSTORE_LAST ...
int ly_log_options(int);

LY_LOG_LEVEL ly_log_level(LY_LOG_LEVEL);
extern "Python" void lypy_log_cb(LY_LOG_LEVEL, const char *, const char *, const char *, uint64_t);
void ly_set_log_clb(void (*)(LY_LOG_LEVEL, const char *, const char *, const char *, uint64_t));
const struct ly_err_item *ly_err_first(const struct ly_ctx *);
const struct ly_err_item *ly_err_last(const struct ly_ctx *);
void ly_err_clean(struct ly_ctx *, struct ly_err_item *);

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
struct lys_module* ly_ctx_get_module_latest(const struct ly_ctx *, const char *);
LY_ERR ly_ctx_compile(struct ly_ctx *);

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
    struct lysc_ext_instance *exts;
    void *priv;
    ...;
};

struct ly_err_item {
    LY_LOG_LEVEL level;
    LY_ERR err;
    LY_VECODE vecode;
    char *msg;
    char *data_path;
    char *schema_path;
    uint64_t line;
    char *apptag;
    struct ly_err_item *next;
    struct ly_err_item *prev;
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

#define LYD_NEW_VAL_OUTPUT ...
#define LYD_NEW_VAL_STORE_ONLY ...
#define LYD_NEW_VAL_BIN ...
#define LYD_NEW_VAL_CANON ...
#define LYD_NEW_META_CLEAR_DFLT ...
#define LYD_NEW_PATH_UPDATE ...
#define LYD_NEW_PATH_OPAQ ...
LY_ERR lyd_new_path(struct lyd_node *, const struct ly_ctx *, const char *, const char *, uint32_t, struct lyd_node **);
LY_ERR lyd_find_xpath(const struct lyd_node *, const char *, struct ly_set **);
void lyd_unlink_siblings(struct lyd_node *node);
void lyd_unlink_tree(struct lyd_node *node);
void lyd_free_all(struct lyd_node *node);
void lyd_free_tree(struct lyd_node *node);

typedef enum {
    LYD_UNKNOWN,
    LYD_XML,
    LYD_JSON,
    LYD_LYB
} LYD_FORMAT;

enum lyd_type {
    LYD_TYPE_DATA_YANG,
    LYD_TYPE_RPC_YANG,
    LYD_TYPE_NOTIF_YANG,
    LYD_TYPE_REPLY_YANG,
    LYD_TYPE_RPC_NETCONF,
    LYD_TYPE_NOTIF_NETCONF,
    LYD_TYPE_REPLY_NETCONF
};

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
#define LYD_PARSE_STORE_ONLY ...
#define LYD_PARSE_ONLY ...
#define LYD_PARSE_OPAQ ...
#define LYD_PARSE_OPTS_MASK ...
#define LYD_PARSE_ORDERED ...
#define LYD_PARSE_STRICT ...

#define LYD_VALIDATE_NO_STATE ...
#define LYD_VALIDATE_PRESENT ...
#define LYD_VALIDATE_OPTS_MASK ...
#define LYD_VALIDATE_MULTI_ERROR ...

LY_ERR lyd_parse_data_mem(const struct ly_ctx *, const char *, LYD_FORMAT, uint32_t, uint32_t, struct lyd_node **);

struct ly_in;
struct ly_out;
typedef uint8_t ly_bool;
void ly_in_free(struct ly_in *, ly_bool);
void ly_out_free(struct ly_out *, void(*)(void *arg), ly_bool);
ly_bool lyd_node_should_print(const struct lyd_node *node, uint32_t options);
LY_ERR ly_in_new_memory(const char *, struct ly_in **);
LY_ERR ly_in_new_filepath(const char *, size_t, struct ly_in **);
LY_ERR ly_in_new_fd(int, struct ly_in **);
LY_ERR ly_in_new_file(FILE *, struct ly_in **);
LY_ERR ly_out_new_memory(char **, size_t, struct ly_out **);
LY_ERR ly_out_new_filepath(const char *, struct ly_out **);
LY_ERR ly_out_new_file(FILE *, struct ly_out **);
LY_ERR ly_out_new_fd(int, struct ly_out **);

LY_ERR lyd_parse_data(const struct ly_ctx *, struct lyd_node *, struct ly_in *, LYD_FORMAT, uint32_t, uint32_t, struct lyd_node **);
LY_ERR lyd_parse_op(const struct ly_ctx *, struct lyd_node *, struct ly_in *, LYD_FORMAT, enum lyd_type, struct lyd_node **, struct lyd_node **);

typedef enum {
   LYS_OUT_UNKNOWN,
   LYS_OUT_YANG,
   LYS_OUT_YANG_COMPILED,
   LYS_OUT_YIN,
   LYS_OUT_TREE
} LYS_OUTFORMAT;

LY_ERR lys_print_mem(char **, const struct lys_module *, LYS_OUTFORMAT, uint32_t);
LY_ERR lys_print_module(struct ly_out *, const struct lys_module *, LYS_OUTFORMAT, size_t, uint32_t);

#define LYS_PRINT_NO_SUBSTMT ...
#define LYS_PRINT_SHRINK ...

struct lys_module {
    const char *name;
    const char *revision;
    const char *ns;
    const char *prefix;
    const char *filepath;
    const char *org;
    const char *contact;
    const char *dsc;
    const char *ref;
    struct lysp_module *parsed;
    struct lysc_module *compiled;
    struct lysc_ident *identities;
    struct lys_module **augmented_by;
    struct lys_module **deviated_by;
    ly_bool implemented;
    ly_bool to_compile;
    uint8_t latest_revision;
    ...;
};

struct lysp_module {
    struct lys_module *mod;
    struct lysp_revision *revs;
    struct lysp_import *imports;
    struct lysp_include *includes;
    struct lysp_ext *extensions;
    struct lysp_feature *features;
    struct lysp_ident *identities;
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node *data;
    struct lysp_node_augment *augments;
    struct lysp_node_action *rpcs;
    struct lysp_node_notif *notifs;
    struct lysp_deviation *deviations;
    struct lysp_ext_instance *exts;
    uint8_t version;
    uint8_t parsing : 1;
    uint8_t is_submod : 1;
};

const struct lysc_node *lys_getnext(const struct lysc_node *, const struct lysc_node *, const struct lysc_module *, uint32_t);

struct lysc_node_container {
    union {
        struct lysc_node node;
        struct {
            uint16_t nodetype;
            uint16_t flags;
            struct lys_module *module;
            struct lysc_node *parent;
            struct lysc_node *next;
            struct lysc_node *prev;
            const char *name;
            const char *dsc;
            const char *ref;
            struct lysc_ext_instance *exts;
            void *priv;
            ...;
        };
    };

    struct lysc_node *child;
    struct lysc_must *musts;
    struct lysc_when **when;
    struct lysc_node_action *actions;
    struct lysc_node_notif *notifs;
};

struct lysp_ext_instance {
    const char *name;
    const char *argument;
    LY_VALUE_FORMAT format;
    void *prefix_data;
    struct lysp_ext *def;
    void *parent;
    enum ly_stmt parent_stmt;
    uint64_t parent_stmt_index;
    uint16_t flags;
    const struct lyplg_ext_record *record;
    struct lysp_ext_substmt *substmts;
    void *parsed;
    struct lysp_stmt *child;
    struct lysp_ext_instance *exts;
};

 struct lysp_import {
    struct lys_module *module;
    const char *name;
    const char *prefix;
    const char *dsc;
    const char *ref;
    struct lysp_ext_instance *exts;
    uint16_t flags;
    char rev[LY_REV_SIZE];
};

struct lysp_feature {
    const char *name;
    struct lysp_qname *iffeatures;
    struct lysc_iffeature *iffeatures_c;
    struct lysp_feature **depfeatures;
    const char *dsc;
    const char *ref;
    struct lysp_ext_instance *exts;
    uint16_t flags;
};

LY_ERR lys_feature_value(const struct lys_module *, const char *);
struct lysp_feature* lysp_feature_next(const struct lysp_feature *, const struct lysp_module *, uint32_t *);

#define LYS_CONFIG_W ...
#define LYS_CONFIG_R ...
#define LYS_CONFIG_MASK ...
#define LYS_STATUS_CURR ...
#define LYS_STATUS_DEPRC ...
#define LYS_STATUS_OBSLT ...
#define LYS_STATUS_MASK ...
#define LYS_MAND_TRUE ...
#define LYS_MAND_FALSE ...
#define LYS_MAND_MASK ...
#define LYS_PRESENCE ...
#define LYS_UNIQUE ...
#define LYS_KEY ...
#define LYS_KEYLESS ...
#define LYS_FENABLED ...
#define LYS_ORDBY_SYSTEM ...
#define LYS_ORDBY_USER ...
#define LYS_ORDBY_MASK ...
#define LYS_YINELEM_TRUE ...
#define LYS_YINELEM_FALSE ...
#define LYS_YINELEM_MASK ...
#define LYS_USED_GRP ...
#define LYS_SET_VALUE ...
#define LYS_SET_MIN ...
#define LYS_SET_MAX ...
#define LYS_SET_BASE ...
#define LYS_SET_BIT ...
#define LYS_SET_ENUM ...
#define LYS_SET_FRDIGITS ...
#define LYS_SET_LENGTH ...
#define LYS_SET_PATH ...
#define LYS_SET_PATTERN ...
#define LYS_SET_RANGE ...
#define LYS_SET_TYPE ...
#define LYS_SET_REQINST ...
#define LYS_SET_DFLT ...
#define LYS_SET_UNITS ...
#define LYS_SET_CONFIG ...
#define LYS_SINGLEQUOTED ...
#define LYS_DOUBLEQUOTED ...
#define LYS_YIN_ATTR ...
#define LYS_YIN_ARGUMENT ...
#define LYS_INTERNAL ...
#define LYS_IS_ENUM ...
#define LYS_IS_INPUT ...
#define LYS_IS_OUTPUT ...
#define LYS_IS_NOTIF ...

#define LY_REV_SIZE 11

struct lysp_revision {
    char date[LY_REV_SIZE];
    const char *dsc;
    const char *ref;
    struct lysp_ext_instance *exts;
};

typedef enum {
    LYSC_PATH_LOG,
    LYSC_PATH_DATA,
    LYSC_PATH_DATA_PATTERN
} LYSC_PATH_TYPE;

char* lysc_path(const struct lysc_node *, LYSC_PATH_TYPE, char *, size_t);

struct lysp_when {
    const char *cond;
    ...;
};

struct lysp_refine {
    const char *nodeid;
    const char *dsc;
    const char *ref;
    struct lysp_qname *iffeatures;
    struct lysp_restr *musts;
    const char *presence;
    struct lysp_qname *dflts;
    uint32_t min;
    uint32_t max;
    struct lysp_ext_instance *exts;
    uint16_t flags;
};

struct lysp_node_container {
    struct lysp_restr *musts;
    struct lysp_when *when;
    const char *presence;
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node *child;
    struct lysp_node_action *actions;
    struct lysp_node_notif *notifs;
    ...;
};

struct lysc_node_leaf {
    union {
        struct lysc_node node;
        struct {
            void *priv;
            uint16_t flags;
            ...;
        };
    };
    struct lysc_must *musts;
    struct lysc_when **when;
    struct lysc_type *type;
    const char *units;
    struct lyd_value *dflt;
    ...;
};

struct lysp_node_leaf {
    struct lysp_restr *musts;
    struct lysp_when *when;
    struct lysp_type type;
    const char *units;
    struct lysp_qname dflt;
    ...;
};

struct lysc_node_list {
    struct lysc_node *child;
    struct lysc_must *musts;
    struct lysc_when **when;
    struct lysc_node_action *actions;
    struct lysc_node_notif *notifs;
    struct lysc_node_leaf ***uniques;
    uint32_t min;
    uint32_t max;
    ...;
};

struct lysc_node_leaflist {
    struct lysc_must *musts;
    struct lysc_when **when;
    struct lysc_type *type;
    const char *units;
    struct lyd_value **dflts;
    uint32_t min;
    uint32_t max;
    ...;
};

struct lysp_node_leaflist {
    struct lysp_restr *musts;
    struct lysp_when *when;
    struct lysp_type type;
    const char *units;
    struct lysp_qname *dflts;
    uint32_t min;
    uint32_t max;
    ...;
};

struct lysp_node_list {
    struct lysp_restr *musts;
    struct lysp_when *when;
    const char *key;
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node *child;
    struct lysp_node_action *actions;
    struct lysp_node_notif *notifs;
    struct lysp_qname *uniques;
    uint32_t min;
    uint32_t max;
    ...;
};

struct lysp_node_choice {
    struct lysp_node *child;
    struct lysp_when *when;
    struct lysp_qname dflt;
    ...;
};

struct lysp_node_case {
    struct lysp_node *child;
    struct lysp_when *when;
    ...;
};

struct lysp_node_anydata {
    struct lysp_restr *musts;
    struct lysp_when *when;
    ...;
};

struct lysp_node_uses {
    struct lysp_refine *refines;
    struct lysp_node_augment *augments;
    struct lysp_when *when;
    ...;
};

struct lysp_node_action_inout {
    struct lysp_restr *musts;
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node *child;
    ...;
};

struct lysp_node_action {
    union {
        struct lysp_node node;
        struct {
            struct lysp_node_action *next;
            ...;
        };
    };
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node_action_inout input;
    struct lysp_node_action_inout output;
    ...;
};

struct lysp_node_notif {
    union {
        struct lysp_node node;
        struct {
            struct lysp_node_notif *next;
            ...;
        };
    };
    struct lysp_restr *musts;
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node *child;
    ...;
};

struct lysp_node_grp {
    union {
        struct lysp_node node;
        struct {
            struct lysp_node_grp *next;
            ...;
        };
    };
    struct lysp_tpdf *typedefs;
    struct lysp_node_grp *groupings;
    struct lysp_node *child;
    struct lysp_node_action *actions;
    struct lysp_node_notif *notifs;
    ...;
};

struct lysp_node_augment {
    union {
        struct lysp_node node;
        struct {
            struct lysp_node_augment *next;
            ...;
        };
    };
    struct lysp_node *child;
    struct lysp_when *when;
    struct lysp_node_action *actions;
    struct lysp_node_notif *notifs;
    ...;
};

struct lysc_type {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
};

struct lysp_type_enum {
    const char *name;
    const char *dsc;
    const char *ref;
    int64_t value;
    struct lysp_qname *iffeatures;
    struct lysp_ext_instance *exts;
    uint16_t flags;
};

struct lysp_type {
    const char *name;
    struct lysp_restr *range;
    struct lysp_restr *length;
    struct lysp_restr *patterns;
    struct lysp_type_enum *enums;
    struct lysp_type_enum *bits;
    struct lyxp_expr *path;
    const char **bases;
    struct lysp_type *types;
    struct lysp_ext_instance *exts;
    const struct lysp_module *pmod;
    struct lysc_type *compiled;
    uint8_t fraction_digits;
    uint8_t require_instance;
    uint16_t flags;
};

struct lysp_qname {
    const char *str;
    const struct lysp_module *mod;
    ...;
};

struct lysp_node {
    struct lysp_node *parent;
    uint16_t nodetype;
    uint16_t flags;
    struct lysp_node *next;
    const char *name;
    const char *dsc;
    const char *ref;
    struct lysp_qname *iffeatures;
    struct lysp_ext_instance *exts;
};

#define LYS_IFF_NOT ...
#define LYS_IFF_AND ...
#define LYS_IFF_OR ...
#define LYS_IFF_F ...
struct lysc_iffeature {
    uint8_t *expr;
    struct lysp_feature **features;
};

struct lysc_ext_instance {
    struct lysc_ext *def;
    const char *argument;
    struct lys_module *module;
    struct lysc_ext_instance *exts;
    void *parent;
    enum ly_stmt parent_stmt;
    uint64_t parent_stmt_index;
    struct lysc_ext_substmt *substmts;
    void *compiled;
};

struct lysc_ext {
    const char *name;
    const char *argname;
    struct lysc_ext_instance *exts;
    struct lyplg_ext *plugin;
    struct lys_module *module;
    uint16_t flags;
};

#define LYS_GETNEXT_WITHCHOICE ...
#define LYS_GETNEXT_NOCHOICE ...
#define LYS_GETNEXT_WITHCASE ...
#define LYS_GETNEXT_INTONPCONT ...
#define LYS_GETNEXT_OUTPUT ...
#define LYS_GETNEXT_WITHSCHEMAMOUNT ...

const struct lysc_node* lys_find_child(const struct lysc_node *, const struct lys_module *, const char *, size_t, uint16_t, uint32_t);
const struct lysc_node* lysc_node_child(const struct lysc_node *);
const struct lysc_node_action* lysc_node_actions(const struct lysc_node *);
const struct lysc_node_notif* lysc_node_notifs(const struct lysc_node *);

typedef enum {
    LYD_PATH_STD,
    LYD_PATH_STD_NO_LAST_PRED
} LYD_PATH_TYPE;

LY_ERR lyd_new_term(struct lyd_node *, const struct lys_module *, const char *, const char *, uint32_t, struct lyd_node **);
char* lyd_path(const struct lyd_node *, LYD_PATH_TYPE, char *, size_t);
LY_ERR lyd_new_inner(struct lyd_node *, const struct lys_module *, const char *, ly_bool, struct lyd_node **);
LY_ERR lyd_new_list(struct lyd_node *, const struct lys_module *, const char *, uint32_t, struct lyd_node **node, ...);

struct lyd_node_inner {
    union {
        struct lyd_node node;
        struct {
            uint32_t hash;
            uint32_t flags;
            const struct lysc_node *schema;
            struct lyd_node_inner *parent;
            struct lyd_node *next;
            struct lyd_node *prev;
            struct lyd_meta *meta;
            void *priv;
        };
    };
    struct lyd_node *child;
    ...;
};

LY_ERR lyd_validate_all(struct lyd_node **, const struct ly_ctx *, uint32_t, struct lyd_node **);
LY_ERR lyd_validate_op(struct lyd_node *, const struct lyd_node *, enum lyd_type, struct lyd_node **);
struct lyd_node* lyd_child_no_keys(const struct lyd_node *);

struct lyd_node_term {
    union {
        struct lyd_node node;
        struct {
            uint32_t hash;
            uint32_t flags;
            const struct lysc_node *schema;
            struct lyd_node_inner *parent;
            struct lyd_node *next;
            struct lyd_node *prev;
            struct lyd_meta *meta;
            void *priv;
        };
    };
    struct lyd_value value;
};

struct lyd_value {
    const struct lysc_type *realtype;
    union {
        int8_t boolean;
        int64_t dec64;
        int8_t int8;
        int16_t int16;
        int32_t int32;
        int64_t int64;
        uint8_t uint8;
        uint16_t uint16;
        uint32_t uint32;
        uint64_t uint64;
        struct lysc_type_bitenum_item *enum_item;
        struct lysc_ident *ident;
        struct ly_path *target;
        struct lyd_value_union *subvalue;
        void *dyn_mem;
        ...;
    };
    ...;
};

struct lyd_value_union {
    struct lyd_value value;
    ...;
};

const char * lyd_get_value(const struct lyd_node *);
struct lyd_node* lyd_child(const struct lyd_node *);
LY_ERR lyd_find_path(const struct lyd_node *, const char *, ly_bool, struct lyd_node **);
void lyd_free_siblings(struct lyd_node *);
struct lyd_node* lyd_first_sibling(const struct lyd_node *);

#define LYD_DIFF_DEFAULTS ...
LY_ERR lyd_diff_siblings(const struct lyd_node *, const struct lyd_node *, uint16_t, struct lyd_node **);
LY_ERR lyd_diff_tree(const struct lyd_node *, const struct lyd_node *, uint16_t, struct lyd_node **);

struct lysc_must* lysc_node_musts(const struct lysc_node *);
struct lysc_must {
    struct lyxp_expr *cond;
    struct lysc_prefix *prefixes;
    const char *dsc;
    const char *ref;
    const char *emsg;
    const char *eapptag;
    struct lysc_ext_instance *exts;
};

struct pcre2_real_code;
typedef struct pcre2_real_code pcre2_code;

struct lysc_pattern {
    const char *expr;
    pcre2_code *code;
    const char *dsc;
    const char *ref;
    const char *emsg;
    const char *eapptag;
    struct lysc_ext_instance *exts;
    uint32_t inverted : 1;
    uint32_t refcount : 31;
};

#define LYSP_RESTR_PATTERN_ACK ...
#define LYSP_RESTR_PATTERN_NACK ...

struct lysp_restr {
    struct lysp_qname arg;
    const char *emsg;
    const char *eapptag;
    const char *dsc;
    const char *ref;
    struct lysp_ext_instance *exts;
};

struct lysc_type_num {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_range *range;
};

struct lysc_type_dec {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    uint8_t fraction_digits;
    struct lysc_range *range;
};

struct lysc_type_str {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_range *length;
    struct lysc_pattern **patterns;
};

struct lysc_type_bitenum_item {
    const char *name;
    const char *dsc;
    const char *ref;
    struct lysc_ext_instance *exts;
    union {
        int32_t value;
        uint32_t position;
    };
    uint16_t flags;
};

struct lysc_type_enum {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_type_bitenum_item *enums;
};

struct lysc_type_bits {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_type_bitenum_item *bits;
};

struct lysc_type_leafref {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lyxp_expr *path;
    struct lysc_prefix *prefixes;
    struct lysc_type *realtype;
    uint8_t require_instance;
};

struct lysc_type_identityref {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_ident **bases;
};

struct lysc_type_instanceid {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    uint8_t require_instance;
};

struct lysc_type_union {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_type **types;
};

struct lysc_type_bin {
    const char *name;
    struct lysc_ext_instance *exts;
    struct lyplg_type *plugin;
    LY_DATA_TYPE basetype;
    uint32_t refcount;
    struct lysc_range *length;
};

const struct lysc_node* lys_find_path(const struct ly_ctx *, const struct lysc_node *, const char *, ly_bool);
const char* lyxp_get_expr(const struct lyxp_expr *);
const char* lyd_value_get_canonical(const struct ly_ctx *, const struct lyd_value *);

#define LYS_FIND_XP_SCHEMA ...
#define LYS_FIND_XP_OUTPUT ...
#define LYS_FIND_NO_MATCH_ERROR ...

typedef enum {
    LYS_IN_UNKNOWN = 0,
    LYS_IN_YANG = 1,
    LYS_IN_YIN = 3
} LYS_INFORMAT;

LY_ERR lys_parse(struct ly_ctx *, struct ly_in *, LYS_INFORMAT, const char **, struct lys_module **);
LY_ERR ly_ctx_new_ylpath(const char *, const char *, LYD_FORMAT, int, struct ly_ctx **);
LY_ERR ly_ctx_get_yanglib_data(const struct ly_ctx *, struct lyd_node **, const char *, ...);
typedef void (*ly_module_imp_data_free_clb)(void *, void *);
typedef LY_ERR (*ly_module_imp_clb)(const char *, const char *, const char *, const char *, void *, LYS_INFORMAT *, const char **, ly_module_imp_data_free_clb *);
void ly_ctx_set_module_imp_clb(struct ly_ctx *, ly_module_imp_clb, void *);
extern "Python" void lypy_module_imp_data_free_clb(void *, void *);
extern "Python" LY_ERR lypy_module_imp_clb(const char *, const char *, const char *, const char *, void *, LYS_INFORMAT *, const char **, ly_module_imp_data_free_clb *);

LY_ERR lydict_insert(const struct ly_ctx *, const char *, size_t, const char **);
LY_ERR lydict_remove(const struct ly_ctx *, const char *);

struct lyd_meta {
    struct lyd_node *parent;
    struct lyd_meta *next;
    struct lysc_ext_instance *annotation;
    const char *name;
    struct lyd_value value;
};

typedef enum {
   LYD_ANYDATA_DATATREE,
   LYD_ANYDATA_STRING,
   LYD_ANYDATA_XML,
   LYD_ANYDATA_JSON,
   LYD_ANYDATA_LYB
} LYD_ANYDATA_VALUETYPE;

union lyd_any_value {
    struct lyd_node *tree;
    const char *str;
    const char *xml;
    const char *json;
    char *mem;
};

struct lyd_node_any {
    union {
        struct lyd_node node;
        struct {
            uint32_t hash;
            uint32_t flags;
            const struct lysc_node *schema;
            struct lyd_node_inner *parent;
            struct lyd_node *next;
            struct lyd_node *prev;
            struct lyd_meta *meta;
            void *priv;
        };
    };
    union lyd_any_value value;
    LYD_ANYDATA_VALUETYPE value_type;
};

LY_ERR lyd_any_value_str(const struct lyd_node *, char **);

#define LYD_MERGE_DEFAULTS ...
#define LYD_MERGE_DESTRUCT ...
#define LYD_MERGE_WITH_FLAGS ...

LY_ERR lyd_merge_tree(struct lyd_node **, const struct lyd_node *, uint16_t);
LY_ERR lyd_merge_siblings(struct lyd_node **, const struct lyd_node *, uint16_t);
LY_ERR lyd_insert_child(struct lyd_node *, struct lyd_node *);
LY_ERR lyd_insert_sibling(struct lyd_node *, struct lyd_node *, struct lyd_node **);
LY_ERR lyd_insert_after(struct lyd_node *, struct lyd_node *);
LY_ERR lyd_insert_before(struct lyd_node *, struct lyd_node *);
LY_ERR lyd_diff_apply_all(struct lyd_node **, const struct lyd_node *);

#define LYD_DUP_NO_META  ...
#define LYD_DUP_RECURSIVE  ...
#define LYD_DUP_WITH_FLAGS  ...
#define LYD_DUP_WITH_PARENTS  ...

LY_ERR lyd_dup_siblings(const struct lyd_node *, struct lyd_node_inner *, uint32_t, struct lyd_node **);
LY_ERR lyd_dup_single(const struct lyd_node *, struct lyd_node_inner *, uint32_t, struct lyd_node **);
void lyd_free_meta_single(struct lyd_meta *);

struct lysp_tpdf {
    const char *name;
    const char *units;
    struct lysp_qname dflt;
    const char *dsc;
    const char *ref;
    struct lysp_ext_instance *exts;
    struct lysp_type type;
    uint16_t flags;
};

struct lysc_when {
    struct lyxp_expr *cond;
    struct lysc_node *context;
    struct lysc_prefix *prefixes;
    const char *dsc;
    const char *ref;
    struct lysc_ext_instance *exts;
    uint32_t refcount;
    uint16_t flags;
};

struct lysc_when** lysc_node_when(const struct lysc_node *);

struct lysc_node_case {
    struct lysc_node *child;
    struct lysc_when **when;
    ...;
};

struct lysc_node_choice {
    struct lysc_node_case *cases;
    struct lysc_when **when;
    struct lysc_node_case *dflt;
    ...;
};

#define LYD_DEFAULT ...
#define LYD_WHEN_TRUE ...
#define LYD_NEW ...

LY_ERR lyd_eval_xpath(const struct lyd_node *, const char *, ly_bool *);

typedef LY_ERR(* lyd_merge_cb)(struct lyd_node *, const struct lyd_node *, void *);
LY_ERR lyd_merge_module(struct lyd_node **, const struct lyd_node *, const struct lys_module *, lyd_merge_cb, void *, uint16_t);

#define LYD_IMPLICIT_NO_STATE ...
#define LYD_IMPLICIT_NO_CONFIG ...
#define LYD_IMPLICIT_OUTPUT ...
#define LYD_IMPLICIT_NO_DEFAULTS ...

LY_ERR lyd_new_implicit_tree(struct lyd_node *, uint32_t, struct lyd_node **);
LY_ERR lyd_new_implicit_module(struct lyd_node **, const struct lys_module *, uint32_t, struct lyd_node **);
LY_ERR lyd_new_implicit_all(struct lyd_node **, const struct ly_ctx *, uint32_t, struct lyd_node **);

LY_ERR lyd_new_meta(const struct ly_ctx *, struct lyd_node *, const struct lys_module *, const char *, const char *, uint32_t, struct lyd_meta **);

struct ly_opaq_name {
    const char *name;
    const char *prefix;

    union {
        const char *module_ns;
        const char *module_name;
    };
};

struct lyd_node_opaq {
    union {
        struct lyd_node node;

        struct {
            uint32_t hash;
            uint32_t flags;
            const struct lysc_node *schema;
            struct lyd_node_inner *parent;
            struct lyd_node *next;
            struct lyd_node *prev;
            struct lyd_meta *meta;
            void *priv;
        };
    };

    struct lyd_node *child;

    struct ly_opaq_name name;
    const char *value;
    uint32_t hints;
    LY_VALUE_FORMAT format;
    void *val_prefix_data;

    struct lyd_attr *attr;
    const struct ly_ctx *ctx;
};

struct lyd_attr {
    struct lyd_node_opaq *parent;
    struct lyd_attr *next;
    struct ly_opaq_name name;
    const char *value;
    uint32_t hints;
    LY_VALUE_FORMAT format;
    void *val_prefix_data;
};

LY_ERR lyd_new_attr(struct lyd_node *, const char *, const char *, const char *, struct lyd_attr **);
void lyd_free_attr_single(const struct ly_ctx *ctx, struct lyd_attr *attr);

struct lyd_leafref_links_rec {
    const struct lyd_node_term *node;
    const struct lyd_node_term **leafref_nodes;
    const struct lyd_node_term **target_nodes;
};

LY_ERR lyd_leafref_get_links(const struct lyd_node_term *e, const struct lyd_leafref_links_rec **);
LY_ERR lyd_leafref_link_node_tree(struct lyd_node *);

/* from libc, needed to free allocated strings */
void free(void *);
