/**
 * Copyright (c) 2020 CESNET, z.s.p.o.
 * SPDX-License-Identifier: MIT
 * Author David Sedlák
*/

struct ly_ctx;
struct lys_module;

struct lysc_node {
    uint16_t nodetype;               /**< type of the node (mandatory) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) */
    struct lys_module *module;       /**< module structure */
    struct lysc_node *parent;        /**< parent node (NULL in case of top level node) */
    struct lysc_node *next;          /**< next sibling node (NULL if there is no one) */
    struct lysc_node *prev;          /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
    const char *name;                /**< node name (mandatory) */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    ...;
};

struct lysc_node_action_inout {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_INPUT or LYS_OUTPUT */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent;/**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (output node for input, NULL for output) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node (input and output node pointing to each other) */
            const char *name;        /**< "input" or "output" */
            const char *dsc;         /**< ALWAYS NULL, compatibility member with ::lysc_node */
            const char *ref;         /**< ALWAYS NULL, compatibility member with ::lysc_node */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_node *child;         /**< first child node (linked list) */
    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    ...;
};

struct lysc_node_action {
    union {
        struct lysc_node node;               /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_RPC or LYS_ACTION */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node - RPC) */
            struct lysc_node_action *next; /**< next sibling node (NULL if there is no one) */
            struct lysc_node_action *prev; /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< action/RPC name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)),
                                          the action/RPC nodes do not contain the when statement on their own, but they can
                                          inherit it from the parent's uses. */
    struct lysc_node_action_inout input;  /**< RPC's/action's input */
    struct lysc_node_action_inout output; /**< RPC's/action's output */
    ...;
};

struct lysc_node_notif {
    union {
        struct lysc_node node;                       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_NOTIF */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node_notif *next; /**< next sibling node (NULL if there is no one) */
            struct lysc_node_notif *prev; /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< Notification name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_node *child;         /**< first child node (linked list) */
    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)),
                                          the notification nodes do not contain the when statement on their own, but they can
                                          inherit it from the parent's uses. */
    ...;
};

struct lysc_node_container {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_CONTAINER */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_node *child;         /**< first child node (linked list) */
    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    struct lysc_node_action *actions;/**< first of actions nodes (linked list) */
    struct lysc_node_notif *notifs;  /**< first of notifications nodes (linked list) */
    ...;
};

struct lysc_node_case {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_CASE */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< name of the case, including the implicit case */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_node *child;         /**< first child node of the case (linked list). Note that all the children of all the sibling cases are linked
                                          each other as siblings with the parent pointer pointing to appropriate case node. */
    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    ...;
};

struct lysc_node_choice {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_CHOICE */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_node_case *cases;    /**< list of the cases (linked list). Note that all the children of all the cases are linked each other
                                          as siblings. Their parent pointers points to the specific case they belongs to, so distinguish the
                                          case is simple. */
    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    struct lysc_node_case *dflt;     /**< default case of the choice, only a pointer into the cases array. */
    ...;
};

struct lysc_node_leaf {
    union {
        struct lysc_node node;               /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_LEAF */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    struct lysc_type *type;          /**< type of the leaf node (mandatory) */

    const char *units;               /**< units of the leaf's type */
    struct lyd_value *dflt;          /**< default value */
    ...;
};

struct lysc_node_leaflist {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_LEAFLIST */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysc_when **when;         /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    struct lysc_type *type;          /**< type of the leaf node (mandatory) */

    const char *units;               /**< units of the leaf's type */
    struct lyd_value **dflts;        /**< list ([sized array](@ref sizedarrays)) of default values */

    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint */
    ...;
};

struct lysc_node_list {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_LIST */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_node *child;         /**< first child node (linked list) */
    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysc_when **when; /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    struct lysc_node_action *actions;/**< first of actions nodes (linked list) */
    struct lysc_node_notif *notifs;  /**< first of notifications nodes (linked list) */

    struct lysc_node_leaf ***uniques;/**< list of sized arrays of pointers to the unique nodes ([sized array](@ref sizedarrays)) */
    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint */
};

struct lysc_node_anydata {
    union {
        struct lysc_node node;       /**< implicit cast for the members compatible with ::lysc_node */
        struct {
            uint16_t nodetype;       /**< LYS_ANYXML or LYS_ANYDATA */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lys_module *module; /**< module structure */
            struct lysc_node *parent; /**< parent node (NULL in case of top level node) */
            struct lysc_node *next;  /**< next sibling node (NULL if there is no one) */
            struct lysc_node *prev;  /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description */
            const char *ref;         /**< reference */
            struct lysc_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
            ...;
        };
    };

    struct lysc_must *musts;         /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysc_when **when; /**< list of pointers to when statements ([sized array](@ref sizedarrays)) */
    ...;
};

struct lysc_when {
    struct lyxp_expr *cond;          /**< XPath when condition */
    struct lysc_node *context;       /**< context node for evaluating the expression, NULL if the context is root node */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint32_t refcount;               /**< reference counter since some of the when statements are shared among several nodes */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) - only LYS_STATUS is allowed */
    ...;
};

struct lysc_ext {
    const char *name;                /**< extension name */
    const char *argument;            /**< argument name, NULL if not specified */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    struct lys_module *module;       /**< module structure */
    uint16_t flags;                  /**< LYS_STATUS_* value (@ref snodeflags) */
    ...;
};

struct lysc_must {
    struct lyxp_expr *cond;          /**< XPath when condition */
    struct lysc_prefix *prefixes;    /**< compiled used prefixes in the condition */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    const char *emsg;                /**< error-message */
    const char *eapptag;             /**< error-app-tag value */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};

/**
 * @brief YANG built-in types
 */
typedef enum
{
    LY_TYPE_UNKNOWN, /**< Unknown type */
    LY_TYPE_BINARY, /**< Any binary data ([RFC 6020 sec 9.8](http://tools.ietf.org/html/rfc6020#section-9.8)) */
    LY_TYPE_UINT8, /**< 8-bit unsigned integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_UINT16, /**< 16-bit unsigned integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_UINT32, /**< 32-bit unsigned integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_UINT64, /**< 64-bit unsigned integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_STRING, /**< Human-readable string ([RFC 6020 sec 9.4](http://tools.ietf.org/html/rfc6020#section-9.4)) */
    LY_TYPE_BITS, /**< A set of bits or flags ([RFC 6020 sec 9.7](http://tools.ietf.org/html/rfc6020#section-9.7)) */
    LY_TYPE_BOOL, /**< "true" or "false" ([RFC 6020 sec 9.5](http://tools.ietf.org/html/rfc6020#section-9.5)) */
    LY_TYPE_DEC64, /**< 64-bit signed decimal number ([RFC 6020 sec 9.3](http://tools.ietf.org/html/rfc6020#section-9.3))*/
    LY_TYPE_EMPTY, /**< A leaf that does not have any value ([RFC 6020 sec 9.11](http://tools.ietf.org/html/rfc6020#section-9.11)) */
    LY_TYPE_ENUM, /**< Enumerated strings ([RFC 6020 sec 9.6](http://tools.ietf.org/html/rfc6020#section-9.6)) */
    LY_TYPE_IDENT, /**< A reference to an abstract identity ([RFC 6020 sec 9.10](http://tools.ietf.org/html/rfc6020#section-9.10)) */
    LY_TYPE_INST, /**< References a data tree node ([RFC 6020 sec 9.13](http://tools.ietf.org/html/rfc6020#section-9.13)) */
    LY_TYPE_LEAFREF, /**< A reference to a leaf instance ([RFC 6020 sec 9.9](http://tools.ietf.org/html/rfc6020#section-9.9))*/
    LY_TYPE_UNION, /**< Choice of member types ([RFC 6020 sec 9.12](http://tools.ietf.org/html/rfc6020#section-9.12)) */
    LY_TYPE_INT8, /**< 8-bit signed integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_INT16, /**< 16-bit signed integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_INT32, /**< 32-bit signed integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
    LY_TYPE_INT64, /**< 64-bit signed integer ([RFC 6020 sec 9.2](http://tools.ietf.org/html/rfc6020#section-9.2)) */
} LY_DATA_TYPE;

struct lysc_type {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    ...;
};

struct lysc_type_num {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_range *range;        /**< Optional range limitation */
    ...;
};

struct lysc_type_dec {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    uint8_t fraction_digits;         /**< fraction digits specification */
    struct lysc_range *range;        /**< Optional range limitation */
    ...;
};

struct lysc_type_str {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_range *length;       /**< Optional length limitation */
    struct lysc_pattern **patterns;  /**< Optional list of pointers to pattern limitations ([sized array](@ref sizedarrays)) */
    ...;
};

struct lysc_pattern {
    const char *expr;                /**< original, not compiled, regular expression */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    const char *emsg;                /**< error-message */
    const char *eapptag;             /**< error-app-tag value */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    ...;
};

struct lysc_type_enum {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    struct lysc_type_bitenum_item *enums; /**< enumerations list ([sized array](@ref sizedarrays)), mandatory (at least 1 item) */
    ...;
};

struct lysc_type_bits {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_type_bitenum_item *bits; /**< bits list ([sized array](@ref sizedarrays)), mandatory (at least 1 item),
                                              the items are ordered by their position value. */
    ...;
};

struct lysc_type_bitenum_item {
    const char *name;            /**< enumeration identifier */
    const char *dsc;             /**< description */
    const char *ref;             /**< reference */
    struct lysc_ext_instance *exts;    /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    union {
        int32_t value;           /**< integer value associated with the enumeration */
        uint32_t position;       /**< non-negative integer value associated with the bit */
    };
    uint16_t flags;              /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_ and LYS_SET_VALUE
                                          values are allowed */
};

struct lysc_range {
    struct lysc_range_part {
        union {                      /**< min boundary */
            int64_t min_64;          /**< for int8, int16, int32, int64 and decimal64 ( >= LY_TYPE_DEC64) */
            uint64_t min_u64;        /**< for uint8, uint16, uint32, uint64, string and binary ( < LY_TYPE_DEC64) */
        };
        union {                      /**< max boundary */
            int64_t max_64;          /**< for int8, int16, int32, int64 and decimal64 ( >= LY_TYPE_DEC64) */
            uint64_t max_u64;        /**< for uint8, uint16, uint32, uint64, string and binary ( < LY_TYPE_DEC64) */
        };
    } *parts;                        /**< compiled range expression ([sized array](@ref sizedarrays)) */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    const char *emsg;                /**< error-message */
    const char *eapptag;             /**< error-app-tag value */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};

struct lysc_iffeature {
    ...;
};

struct ly_out;

typedef enum
{
    LY_SUCCESS,     /**< no error, not set by functions, included just to complete #LY_ERR enumeration */
    LY_EMEM,        /**< Memory allocation failure */
    LY_ESYS,        /**< System call failure */
    LY_EINVAL,      /**< Invalid value */
    LY_EEXIST,      /**< Item already exists */
    LY_ENOTFOUND,   /**< Item does not exists */
    LY_EINT,        /**< Internal error */
    LY_EVALID,      /**< Validation failure */
    LY_EDENIED,     /**< Operation is not allowed */
    LY_EINCOMPLETE, /**< The operation did not failed, but for some reason it was not possible to finish it completely.
                         According to the specific use case, the caller is usually supposed to perform the operation again. */
    LY_ENOT,        /**< Negative result */
    LY_EOTHER,      /**< Unknown error */
    LY_EPLUGIN      /**< Error reported by a plugin - the highest bit in the first byte is set.
                         This value is used ORed with one of the other LY_ERR value and can be simply masked. */
} LY_ERR;

typedef enum {
    LYS_IN_UNKNOWN,  /**< unknown format, used as return value in case of error */
    LYS_IN_YANG,     /**< YANG schema input format */
    LYS_IN_YIN,      /**< YIN schema input format */
} LYS_INFORMAT;

LY_ERR ly_ctx_new(const char *, int, struct ly_ctx **);
void ly_ctx_destroy(struct ly_ctx *, void(*)(const struct lysc_node *node, void *priv));
LY_ERR ly_ctx_set_options(struct ly_ctx *, int);
LY_ERR ly_ctx_unset_options(struct ly_ctx *, int);
int ly_ctx_get_options(const struct ly_ctx *);
const struct lys_module* ly_ctx_load_module(struct ly_ctx *, const char *,const char *, const char **);
void ly_ctx_reset_latests(struct ly_ctx *);

const char* const * ly_ctx_get_searchdirs(const struct ly_ctx * ctx);
LY_ERR ly_ctx_set_searchdir(struct ly_ctx *ctx, const char *search_dir);
LY_ERR ly_ctx_unset_searchdir(struct ly_ctx *ctx, const char *value);


struct lys_module* ly_ctx_get_module(const struct ly_ctx *, const char *, const char *);
struct lys_module* ly_ctx_get_module_implemented(const struct ly_ctx * , const char *);
struct lys_module* ly_ctx_get_module_latest(const struct ly_ctx *, const char *);

struct lys_module* ly_ctx_get_module_implemented_ns(const struct ly_ctx *, const char *);
struct lys_module* ly_ctx_get_module_latest_ns(const struct ly_ctx *, const char *);
struct lys_module* ly_ctx_get_module_ns(const struct ly_ctx *, const char *, const char *);

const struct lys_module* ly_ctx_get_module_iter(const struct ly_ctx *, unsigned int *);


LY_ERR lys_parse_fd(struct ly_ctx *, int, LYS_INFORMAT, const struct lys_module **);
LY_ERR lys_parse_mem(struct ly_ctx *, const char *, LYS_INFORMAT, const struct lys_module **);
LY_ERR lys_parse_path(struct ly_ctx *, const char *, LYS_INFORMAT, const struct lys_module **);

 typedef enum {
     LYD_UNKNOWN = 0,
     LYD_XML,
     LYD_JSON,
     LYD_LYB,
 } LYD_FORMAT;


LY_ERR lyd_parse_data_fd(const struct ly_ctx *, int, LYD_FORMAT, int, int, struct lyd_node **);
LY_ERR lyd_parse_data_mem(const struct ly_ctx *, const char *, LYD_FORMAT, int, int, struct lyd_node **);
LY_ERR lyd_parse_data_path(const struct ly_ctx * , const char *, LYD_FORMAT, int, int, struct lyd_node **);

 typedef enum
 {
     LY_LLERR,
     LY_LLWRN,
     LY_LLVRB,
     LY_LLDBG,
 } LY_LOG_LEVEL;

#define LY_LOLOG ...
#define LY_LOSTORE ...

LY_LOG_LEVEL ly_log_level(LY_LOG_LEVEL);
extern "Python" void lypy_log_cb(LY_LOG_LEVEL, const char *, const char *);
void ly_set_log_clb(void (*)(LY_LOG_LEVEL, const char *, const char *), int);
struct ly_err_item* ly_err_first ( const struct ly_ctx *);
void ly_err_clean(struct ly_ctx *, struct ly_err_item * eitem);
int ly_log_options(int);

struct ly_err_item {
    char *msg;
    char *path;
    ...;
};


#define 	LY_CTX_ALL_IMPLEMENTED ...
#define 	LY_CTX_DISABLE_SEARCHDIR_CWD   ...
#define 	LY_CTX_DISABLE_SEARCHDIRS   ...
#define 	LY_CTX_NO_YANGLIBRARY   ...
#define 	LY_CTX_PREFER_SEARCHDIRS   ...

struct lysp_module;
struct lysc_module;

 struct lys_module {
     struct ly_ctx *ctx;
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
     uint8_t implemented;
     uint8_t latest_revision;
     ...;
 };

typedef enum LYS_VERSION {
    LYS_VERSION_UNDEF,  /**< no specific version, YANG 1.0 as default */
    LYS_VERSION_1_0,    /**< YANG 1.0 */
    LYS_VERSION_1_1     /**< YANG 1.1 */
} LYS_VERSION;

#define LYS_STATUS_CURR  ...
#define LYS_STATUS_DEPRC ...
#define LYS_STATUS_OBSLT ...
#define LYS_CONFIG_W ...       /**< config true; also set for input children nodes */
#define LYS_CONFIG_R ...       /**< config false; also set for output and notification children nodes */
#define LYS_YIN ...
#define LYS_SET_REQINST ...
#define LYS_FENABLED ...

#define LYS_UNKNOWN ...        /**< uninitalized unknown statement node */
#define LYS_CONTAINER ...      /**< container statement node */
#define LYS_CHOICE ...         /**< choice statement node */
#define LYS_LEAF ...           /**< leaf statement node */
#define LYS_LEAFLIST ...       /**< leaf-list statement node */
#define LYS_LIST ...           /**< list statement node */
#define LYS_ANYXML ...         /**< anyxml statement node */
#define LYS_ANYDATA ...        /**< anydata statement node, in tests it can be used for both #LYS_ANYXML and #LYS_ANYDATA */

#define LYS_RPC ...             /**< RPC statement node */
#define LYS_ACTION ...          /**< action statement node */
#define LYS_NOTIF ...           /**< notification statement node */

#define LYS_CASE ...           /**< case statement node */
#define LYS_USES ...           /**< uses statement node */
#define LYS_INPUT ...
#define LYS_OUTPUT ...
#define LYS_GROUPING ...
#define LYS_AUGMENT ...


#define LY_REV_SIZE 11
struct lysp_revision {
    char date[LY_REV_SIZE];          /**< revision date (madatory) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};

struct lysp_import {
    struct lys_module *module;       /**< pointer to the imported module
                                          (mandatory, but resolved when the referring module is completely parsed) */
    const char *name;                /**< name of the imported module (mandatory) */
    const char *prefix;              /**< prefix for the data from the imported schema (mandatory) */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    char rev[LY_REV_SIZE];           /**< revision-date of the imported module */
    ...;
};

struct lysp_submodule {
    struct lys_module *mod;          /**< belongs to parent module (submodule - mandatory) */

    struct lysp_revision *revs;      /**< list of the module revisions ([sized array](@ref sizedarrays)), the first revision
                                          in the list is always the last (newest) revision of the module */
    struct lysp_import *imports;     /**< list of imported modules ([sized array](@ref sizedarrays)) */
    struct lysp_include *includes;   /**< list of included submodules ([sized array](@ref sizedarrays)) */
    struct lysp_ext *extensions;     /**< list of extension statements ([sized array](@ref sizedarrays)) */
    struct lysp_feature *features;   /**< list of feature definitions ([sized array](@ref sizedarrays)) */
    struct lysp_ident *identities;   /**< list of identities ([sized array](@ref sizedarrays)) */
    struct lysp_tpdf *typedefs;      /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings;      /**< list of groupings ([sized array](@ref sizedarrays)) */
    struct lysp_node *data;          /**< list of module's top-level data nodes (linked list) */
    struct lysp_node_augment *augments;   /**< list of augments ([sized array](@ref sizedarrays)) */
    struct lysp_node_action *rpcs;        /**< list of RPCs ([sized array](@ref sizedarrays)) */
    struct lysp_node_notif *notifs;       /**< list of notifications ([sized array](@ref sizedarrays)) */
    struct lysp_deviation *deviations; /**< list of deviations ([sized array](@ref sizedarrays)) */
    struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */

    uint8_t version;                 /**< yang-version (LYS_VERSION values) */
    const char *name;                /**< name of the module (mandatory) */
    const char *filepath;            /**< path, if the schema was read from a file, NULL in case of reading from memory */
    const char *prefix;              /**< submodule belongsto prefix of main module (mandatory) */
    const char *org;                 /**< party/company responsible for the module */
    const char *contact;             /**< contact information for the module */
    const char *dsc;                 /**< description of the module */
    const char *ref;                 /**< cross-reference for the module */
    ...;
};

struct lysp_include {
    struct lysp_submodule *submodule;/**< pointer to the parsed submodule structure
                                         (mandatory, but resolved when the referring module is completely parsed) */
    const char *name;                /**< name of the included submodule (mandatory) */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    char rev[LY_REV_SIZE];           /**< revision-date of the included submodule */
};

struct lysc_ext;

struct lysp_ext {
    const char *name;                /**< extension name */
    const char *argument;            /**< argument name, NULL if not specified */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< LYS_STATUS_* and LYS_YINELEM_* values (@ref snodeflags) */

    struct lysc_ext *compiled;       /**< pointer to the compiled extension definition */
};

struct lysp_feature {
    const char *name;                /**< feature name (mandatory) */
    struct lysp_qname *iffeatures;   /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
    struct lysc_iffeature *iffeatures_c;    /**< compiled if-features */
    struct lysp_feature **depfeatures;  /**< list of pointers to other features depending on this one
                                          ([sized array](@ref sizedarrays)) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement  */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_* values and
                                          LYS_FENABLED are allowed */
};

struct lysp_ident {
    const char *name;                /**< identity name (mandatory), including possible prefix */
    struct lysp_qname *iffeatures;   /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
    const char **bases;              /**< list of base identifiers ([sized array](@ref sizedarrays)) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_ values are allowed */
};

struct lysp_type {
    const char *name;                /**< name of the type (mandatory) */
    struct lysp_restr *range;        /**< allowed values range - numerical, decimal64 */
    struct lysp_restr *length;       /**< allowed length of the value - string, binary */
    struct lysp_restr *patterns;     /**< list of patterns ([sized array](@ref sizedarrays)) - string */
    struct lysp_type_enum *enums;    /**< list of enum-stmts ([sized array](@ref sizedarrays)) - enum */
    struct lysp_type_enum *bits;     /**< list of bit-stmts ([sized array](@ref sizedarrays)) - bits */
    struct lyxp_expr *path;          /**< parsed path - leafref */
    const char **bases;              /**< list of base identifiers ([sized array](@ref sizedarrays)) - identityref */
    struct lysp_type *types;         /**< list of sub-types ([sized array](@ref sizedarrays)) - union */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */

    struct lysc_type *compiled;      /**< pointer to the compiled type */

    uint8_t fraction_digits;         /**< number of fraction digits - decimal64 */
    uint8_t require_instance;        /**< require-instance flag - leafref, instance */
    uint16_t flags;                  /**< [schema node flags](@ref spnodeflags) */
    ...;
};

struct lysp_tpdf {
    const char *name;                /**< name of the newly defined type (mandatory) */
    const char *units;               /**< units of the newly defined type */
    struct lysp_qname dflt;         /**< default value of the newly defined type */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    struct lysp_type type;           /**< base type from which the typedef is derived (mandatory) */
    uint16_t flags;                  /**< [schema node flags](@ref spnodeflags) */
};

struct lysp_node {
    struct lysp_node *parent;        /**< parent node (NULL if this is a top-level node) */
    uint16_t nodetype;               /**< type of the node (mandatory) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) */
    struct lysp_node *next;          /**< next sibling node (NULL if there is no one) */
    const char *name;                /**< node name (mandatory) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_qname *iffeatures;   /**< list of if-feature expressions ([sized array](@ref sizedarrays)),
                                          must be qname because of refines */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};


struct lysp_node_container {
    union {
        struct lysp_node node;        /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_CONTAINER */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* container */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_when *when;          /**< when statement */
    const char *presence;            /**< presence description */
    struct lysp_tpdf *typedefs;      /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings; /**< list of groupings (linked list) */
    struct lysp_node *child;         /**< list of data nodes (linked list) */
    struct lysp_node_action *actions;/**< list of actions (linked list) */
    struct lysp_node_notif *notifs;  /**< list of notifications (linked list) */
};

struct lysp_qname {
     const char *str;
     const struct lysp_module *mod;
};

struct lysp_node_leaf {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_LEAF */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* leaf */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_when *when;          /**< when statement */
    struct lysp_type type;           /**< type of the leaf node (mandatory) */
    const char *units;               /**< units of the leaf's type */
    struct lysp_qname dflt;          /**< default value, it may or may not be a qualified name */
};

struct lysp_node_leaflist {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_LEAFLIST */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* leaf-list */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_when *when;          /**< when statement */
    struct lysp_type type;           /**< type of the leaf node (mandatory) */
    const char *units;               /**< units of the leaf's type */
    struct lysp_qname *dflts;        /**< list of default values ([sized array](@ref sizedarrays)), they may or
                                          may not be qualified names */
    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint, 0 means unbounded */
};

struct lysp_node_list {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_LIST */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* list */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_when *when;          /**< when statement */
    const char *key;                 /**< keys specification */
    struct lysp_tpdf *typedefs;      /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings; /**< list of groupings (linked list) */
    struct lysp_node *child;         /**< list of data nodes (linked list) */
    struct lysp_node_action *actions;/**< list of actions (linked list) */
    struct lysp_node_notif *notifs;  /**< list of notifications (linked list) */
    struct lysp_qname *uniques;      /**< list of unique specifications ([sized array](@ref sizedarrays)) */
    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint, 0 means unbounded */
};

struct lysp_node_choice {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_CHOICE */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* choice */
    struct lysp_node *child;         /**< list of data nodes (linked list) */
    struct lysp_when *when;          /**< when statement */
    struct lysp_qname dflt;          /**< default case */
};

struct lysp_node_case {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_CASE */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* case */
    struct lysp_node *child;         /**< list of data nodes (linked list) */
    struct lysp_when *when;          /**< when statement */
};

struct lysp_node_anydata {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_ANYXML or LYS_ANYDATA */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< node name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* anyxml/anydata */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_when *when;          /**< when statement */
};

struct lysp_node_uses {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_USES */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< pointer to the next sibling node (NULL if there is no one) */
            const char *name;        /**< grouping name reference (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* uses */
    struct lysp_refine *refines;     /**< list of uses's refines ([sized array](@ref sizedarrays)) */
    struct lysp_node_augment *augments; /**< list of augments (linked list) */
    struct lysp_when *when;          /**< when statement */
};

struct lysp_node_action_inout {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_INPUT or LYS_OUTPUT */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node *next;  /**< NULL */
            const char *name;        /**< empty string */
            const char *dsc;         /**< ALWAYS NULL, compatibility member with ::lysp_node */
            const char *ref;         /**< ALWAYS NULL, compatibility member with ::lysp_node */
            struct lysp_qname *iffeatures; /**< ALWAYS NULL, compatibility member with ::lysp_node */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* inout */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_tpdf *typedefs;      /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings; /**< list of groupings (linked list) */
    struct lysp_node *child;         /**< list of data nodes (linked list) */
};

struct lysp_node_action {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_RPC or LYS_ACTION */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) */
            struct lysp_node_action *next; /**< pointer to the next action (NULL if there is no one) */
            const char *name;        /**< grouping name reference (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* action */
    struct lysp_tpdf *typedefs;      /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings; /**< list of groupings (linked list) */

    struct lysp_node_action_inout input;  /**< RPC's/Action's input */
    struct lysp_node_action_inout output; /**< RPC's/Action's output */
};

struct lysp_node_notif {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent; /**< parent node (NULL if this is a top-level node) */
            uint16_t nodetype;       /**< LYS_NOTIF */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_* values are allowed */
            struct lysp_node_notif *next; /**< pointer to the next notification (NULL if there is no one) */
            const char *name;        /**< grouping name reference (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                            /**< common part corresponding to ::lysp_node */

    /* notif */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_tpdf *typedefs;      /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings; /**< list of groupings (linked list) */
    struct lysp_node *child;         /**< list of data nodes (linked list) */
};

struct lysp_node_grp {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent;/**< parent node (NULL if this is a top-level grouping) */
            uint16_t nodetype;       /**< LYS_GROUPING */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_* values are allowed */
            struct lysp_node_grp *next; /**< pointer to the next grouping (NULL if there is no one) */
            const char *name;        /**< grouping name (mandatory) */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< ALWAYS NULL, compatibility member with ::lysp_node */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                                /**< common part corresponding to ::lysp_node */

    /* grp */
    struct lysp_tpdf *typedefs;       /**< list of typedefs ([sized array](@ref sizedarrays)) */
    struct lysp_node_grp *groupings;  /**< list of groupings (linked list) */
    struct lysp_node *child;          /**< list of data nodes (linked list) */
    struct lysp_node_action *actions; /**< list of actions (linked list) */
    struct lysp_node_notif *notifs;   /**< list of notifications (linked list) */
};

struct lysp_node_augment {
    union {
        struct lysp_node node;       /**< implicit cast for the members compatible with ::lysp_node */
        struct {
            struct lysp_node *parent;/**< parent node (NULL if this is a top-level augment) */
            uint16_t nodetype;       /**< LYS_AUGMENT */
            uint16_t flags;          /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_* values are allowed */
            struct lysp_node_augment *next; /**< pointer to the next augment (NULL if there is no one) */
            const char *nodeid;      /**< target schema nodeid (mandatory) - absolute for global augments, descendant for uses's augments */
            const char *dsc;         /**< description statement */
            const char *ref;         /**< reference statement */
            struct lysp_qname *iffeatures; /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
            struct lysp_ext_instance *exts; /**< list of the extension instances ([sized array](@ref sizedarrays)) */
        };
    };                                /**< common part corresponding to ::lysp_node */

    struct lysp_node *child;         /**< list of data nodes (linked list) */
    struct lysp_when *when;          /**< when statement */
    struct lysp_node_action *actions;/**< list of actions (linked list) */
    struct lysp_node_notif *notifs;  /**< list of notifications (linked list) */
};

struct lysp_refine {
    const char *nodeid;              /**< target descendant schema nodeid (mandatory) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_qname *iffeatures;   /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    const char *presence;            /**< presence description */
    struct lysp_qname *dflts;        /**< list of default values ([sized array](@ref sizedarrays)) */
    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint, 0 means unbounded */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) */
};

struct lysp_deviation {
    const char *nodeid;              /**< target absolute schema nodeid (mandatory) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_deviate* deviates;   /**< list of deviate specifications (linked list) */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};

struct lysp_ext_instance {
    const char *name;                       /**< extension identifier, including possible prefix */
    const char *argument;                   /**< optional value of the extension's argument */
    void *parent;                           /**< pointer to the parent element holding the extension instance(s), use
                                                 ::lysp_ext_instance#parent_type to access the schema element */
    struct lysp_stmt *child;                /**< list of the extension's substatements (linked list) */
    struct lysc_ext_instance *compiled;     /**< pointer to the compiled data if any - in case the source format is YIN,
                                                 some of the information (argument) are available only after compilation */
    uint8_t yin;                            /** flag for YIN source format, can be set to LYS_YIN */
    ...;
};

struct lysp_when {
    const char *cond;                /**< specified condition (mandatory) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};

struct lysp_restr {
    struct lysp_qname arg;           /**< The restriction expression/value (mandatory);
                                          in case of pattern restriction, the first byte has a special meaning:
                                          0x06 (ACK) for regular match and 0x15 (NACK) for invert-match */
    const char *emsg;                /**< error-message */
    const char *eapptag;             /**< error-app-tag value */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
};

#define LYS_DEV_NOT_SUPPORTED ...
#define LYS_DEV_ADD ...
#define LYS_DEV_DELETE ...
#define LYS_DEV_REPLACE ...
#define LYS_YIN_ATTR ...
#define LYS_MAND_TRUE ...
#define LYS_SET_VALUE ...
#define LYS_SET_REQINST ...
#define LYS_SET_MIN ...
#define LYS_SET_MAX ...
#define LYS_CONFIG_W ...
#define LYS_MAND_TRUE ...
#define LYS_MAND_FALSE ...
#define LYS_SET_VALUE ...

struct lysp_deviate {
    uint8_t mod;
    struct lysp_deviate *next;
    struct lysp_ext_instance *exts;
};

struct lysp_deviate_add {
    uint8_t mod;                     /**< [type](@ref deviatetypes) of the deviate modification */
    struct lysp_deviate *next;       /**< next deviate structure in the list */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    const char *units;               /**< units of the values */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_qname *uniques;            /**< list of uniques specifications ([sized array](@ref sizedarrays)) */
    struct lysp_qname *dflts;              /**< list of default values ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) */
    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint, 0 means unbounded */
};

struct lysp_deviate_del {
    uint8_t mod;                     /**< [type](@ref deviatetypes) of the deviate modification */
    struct lysp_deviate *next;       /**< next deviate structure in the list */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    const char *units;               /**< units of the values */
    struct lysp_restr *musts;        /**< list of must restrictions ([sized array](@ref sizedarrays)) */
    struct lysp_qname *uniques;            /**< list of uniques specifications ([sized array](@ref sizedarrays)) */
    struct lysp_qname *dflts;              /**< list of default values ([sized array](@ref sizedarrays)) */
};

struct lysp_deviate_rpl {
    uint8_t mod;                     /**< [type](@ref deviatetypes) of the deviate modification */
    struct lysp_deviate *next;       /**< next deviate structure in the list */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    struct lysp_type *type;          /**< type of the node */
    const char *units;               /**< units of the values */
    struct lysp_qname dflt;          /**< default value */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) */
    uint32_t min;                    /**< min-elements constraint */
    uint32_t max;                    /**< max-elements constraint, 0 means unbounded */
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
    uint8_t parsing:1;
};

struct lysp_stmt {
    const char *stmt;                /**< identifier of the statement */
    const char *arg;                 /**< statement's argument */
    struct lysp_stmt *next;          /**< link to the next statement */
    struct lysp_stmt *child;         /**< list of the statement's substatements (linked list) */
    uint16_t flags;                  /**< statement flags, can be set to LYS_YIN_ATTR */
    ...;
};

struct lysp_type_enum {
    const char *name;                /**< name (mandatory) */
    const char *dsc;                 /**< description statement */
    const char *ref;                 /**< reference statement */
    int64_t value;                   /**< enum's value or bit's position */
    struct lysp_qname *iffeatures;   /**< list of if-feature expressions ([sized array](@ref sizedarrays)) */
    struct lysp_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_ and LYS_SET_VALUE
                                          values are allowed */
};

struct lysc_type_leafref {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_type *realtype;      /**< pointer to the real (first non-leafref in possible leafrefs chain) type. */
    uint8_t require_instance;        /**< require-instance flag */
    ...;
};

struct lysc_type_identityref {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_ident **bases;       /**< list of pointers to the base identities ([sized array](@ref sizedarrays)),
                                          mandatory (at least 1 item) */
    ...;
};

struct lysc_type_instanceid {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    uint8_t require_instance;        /**< require-instance flag */
    ...;
};

struct lysc_type_union {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_type **types;        /**< list of types in the union ([sized array](@ref sizedarrays)), mandatory (at least 1 item) */
    ...;
};

struct lysc_type_bin {
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    LY_DATA_TYPE basetype;           /**< Base type of the type */
    struct lysc_range *length;       /**< Optional length limitation */
    ...;
};

struct lysc_ident {
    const char *name;                /**< identity name (mandatory), including possible prefix */
    const char *dsc;                 /**< description */
    const char *ref;                 /**< reference */
    struct lys_module *module;       /**< module structure */
    struct lysc_ident **derived;     /**< list of (pointers to the) derived identities ([sized array](@ref sizedarrays)) */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    uint16_t flags;                  /**< [schema node flags](@ref snodeflags) - only LYS_STATUS_ values are allowed */
};

struct lysc_node_action;
struct lysc_node_notif;
struct lysc_ext_instance;


struct lysc_module {
    struct lys_module *mod;
    struct lysc_node *data;
    struct lysc_node_action *rpcs;
    struct lysc_node_notif *notifs;
    struct lysc_ext_instance *exts;
};

struct lysc_ext_instance {
    struct lys_module *module;       /**< module where the extension instantiated is defined */
    struct lysc_ext *def;            /**< pointer to the extension definition */
    const char *argument;            /**< optional value of the extension's argument */
    struct lysc_ext_instance *exts;  /**< list of the extension instances ([sized array](@ref sizedarrays)) */
    ...;
};

int lys_feature_value(const struct lys_module *, const char *);
LY_ERR lys_set_implemented(struct lys_module *, const char **);
int get_array_size(void *array);

struct lyd_value {
    const char *canonical;           /**< Original string representation of the value. It is never NULL, but (canonical) string representation
                                         of the value should be always obtained via the type's printer callback (lyd_value::realtype::plugin::print). */
    ...;
};

#define LYD_VALIDATE_OP_RPC ...
#define LYD_VALIDATE_OP_REPLY ...
#define LYD_VALIDATE_OP_NOTIF ...

#define LYD_VALIDATE_NO_STATE ...
#define LYD_VALIDATE_PRESENT ...

#define LYD_PARSE_LYB_MOD_UPDATE ...
#define LYD_PARSE_NO_STATE ...
#define LYD_PARSE_ONLY ...
#define LYD_PARSE_OPAQ ...
#define LYD_PARSE_STRICT ...

#define LYD_NEW_PATH_OPAQ ...
#define LYD_NEW_PATH_OUTPUT ...
#define LYD_NEW_PATH_UPDATE ...

 typedef enum {
     LYD_ANYDATA_DATATREE,
     LYD_ANYDATA_STRING,
     LYD_ANYDATA_XML,
     LYD_ANYDATA_JSON,
     LYD_ANYDATA_LYB,
 } LYD_ANYDATA_VALUETYPE;

typedef enum {
     LYS_OUT_UNKNOWN = 0,
     LYS_OUT_YANG = 1,
     LYS_OUT_YANG_COMPILED = 2,
     LYS_OUT_YIN = 3,
     LYS_OUT_TREE,
} LYS_OUTFORMAT;

LY_ERR lys_print_mem(char **, const struct lys_module *, LYS_OUTFORMAT, int);

LY_ERR lyd_new_path2(struct lyd_node *, const struct ly_ctx *, const char *, const void * 	value, LYD_ANYDATA_VALUETYPE, int , struct lyd_node **, struct lyd_node **);

LY_ERR lyd_validate_module(struct lyd_node **, const struct lys_module *, int, struct lyd_node **);
LY_ERR lyd_validate_all(struct lyd_node **, const struct ly_ctx *, int, struct lyd_node **);

typedef uint8_t ly_bool;

LY_ERR lyd_new_any(struct lyd_node *, const struct lys_module *, const char *, void *, LYD_ANYDATA_VALUETYPE, ly_bool, struct lyd_node **);
LY_ERR lyd_new_inner(struct lyd_node *, const struct lys_module *, const char *, ly_bool, struct lyd_node **);
LY_ERR lyd_new_list2(struct lyd_node *, const struct lys_module *, const char *, const char *, ly_bool, struct lyd_node **);
LY_ERR lyd_new_term(struct lyd_node *, const struct lys_module *, const char *, const char *, ly_bool, struct lyd_node **);

LY_ERR lyd_new_opaq(struct lyd_node *, const struct ly_ctx *, const char *, const char *, const char *, struct lyd_node **);
LY_ERR lyd_find_xpath(const struct lyd_node *, const char *, struct ly_set **);
LY_ERR lyd_merge_tree(struct lyd_node **, const struct lyd_node *, int);
LY_ERR lyd_merge_siblings(struct lyd_node **, const struct lyd_node *, int);
LY_ERR lyd_dup_siblings(const struct lyd_node *, struct lyd_node_inner *, int, struct lyd_node **);
LY_ERR lyd_insert_child(struct lyd_node *, struct lyd_node *);
LY_ERR lyd_insert_before(struct lyd_node *, struct lyd_node *);
LY_ERR lyd_insert_after(struct lyd_node *, struct lyd_node *);
LY_ERR lyd_insert_sibling(struct lyd_node *, struct lyd_node *, struct lyd_node **);
LY_ERR lyd_print_tree(struct ly_out *, const struct lyd_node *, LYD_FORMAT, int);
LY_ERR lyd_print_all(struct ly_out *, const struct lyd_node *, LYD_FORMAT, int);
void lyd_unlink_tree(struct lyd_node *);
const char *lyd_data_canonic(struct lyd_node_term *);

struct ly_out;
LY_ERR ly_out_new_fd(int, struct ly_out **);
LY_ERR ly_out_new_memory(char **, size_t, struct ly_out **);
void ly_out_free(struct ly_out *, void(*)(void *arg), int);

#define LYS_PRINT_NO_SUBSTMT ...
#define LYS_PRINT_SHRINK ...

const struct lysc_node* lys_getnext(const struct lysc_node *, const struct lysc_node *, const struct lysc_module *, int);

#define LYS_GETNEXT_INTONPCONT ...
#define LYS_GETNEXT_NOCHOICE ...
#define LYS_GETNEXT_OUTPUT ...
#define LYS_GETNEXT_WITHCASE ...
#define LYS_GETNEXT_WITHCHOICE ...

#define LYD_DUP_NO_META ...
#define LYD_DUP_RECURSIVE ...
#define LYD_DUP_WITH_FLAGS ...
#define LYD_DUP_WITH_PARENTS ...

const struct lys_module* lyd_owner_module(const struct lyd_node *);

LY_ERR lyd_compare_single(const struct lyd_node *, const struct lyd_node *, int);

 struct ly_set
 {
     uint32_t count;
     void **objs;
     ...;
 };

struct lyd_node {
    uint32_t hash;                   /**< hash of this particular node (module name + schema name + key string values if list or
                                          hashes of all nodes of subtree in case of keyless list). Note that while hash can be
                                          used to get know that nodes are not equal, it cannot be used to decide that the
                                          nodes are equal due to possible collisions. */
    uint32_t flags;                  /**< [data node flags](@ref dnodeflags) */
    const struct lysc_node *schema;  /**< pointer to the schema definition of this node, note that the target can be not just
                                          ::struct lysc_node but ::struct lysc_node_action or ::struct lysc_node_notif as well */
    struct lyd_node_inner *parent;   /**< pointer to the parent node, NULL in case of root node */
    struct lyd_node *next;           /**< pointer to the next sibling node (NULL if there is no one) */
    struct lyd_node *prev;           /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
    struct lyd_meta *meta;           /**< pointer to the list of metadata of this node */
    ...;
};

struct lyd_node_inner {
    uint32_t hash;                   /**< hash of this particular node (module name + schema name + key string values if list or
                                          hashes of all nodes of subtree in case of keyless list). Note that while hash can be
                                          used to get know that nodes are not equal, it cannot be used to decide that the
                                          nodes are equal due to possible collisions. */
    uint32_t flags;                  /**< [data node flags](@ref dnodeflags) */
    const struct lysc_node *schema;  /**< pointer to the schema definition of this node */
    struct lyd_node_inner *parent;   /**< pointer to the parent node, NULL in case of root node */
    struct lyd_node *next;           /**< pointer to the next sibling node (NULL if there is no one) */
    struct lyd_node *prev;           /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
    struct lyd_meta *meta;           /**< pointer to the list of metadata of this node */
    struct lyd_node *child;          /**< pointer to the first child node. */
    ...;
};

struct lyd_node_term {
    uint32_t hash;                   /**< hash of this particular node (module name + schema name + key string values if list or
                                          hashes of all nodes of subtree in case of keyless list). Note that while hash can be
                                          used to get know that nodes are not equal, it cannot be used to decide that the
                                          nodes are equal due to possible collisions. */
    uint32_t flags;                  /**< [data node flags](@ref dnodeflags) */
    const struct lysc_node *schema;  /**< pointer to the schema definition of this node */
    struct lyd_node_inner *parent;   /**< pointer to the parent node, NULL in case of root node */
    struct lyd_node *next;           /**< pointer to the next sibling node (NULL if there is no one) */
    struct lyd_node *prev;           /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
    struct lyd_meta *meta;           /**< pointer to the list of metadata of this node */
    struct lyd_value value;            /**< node's value representation */
};

struct lyd_node_any {
    uint32_t hash;                   /**< hash of this particular node (module name + schema name + key string values if list or
                                          hashes of all nodes of subtree in case of keyless list). Note that while hash can be
                                          used to get know that nodes are not equal, it cannot be used to decide that the
                                          nodes are equal due to possible collisions. */
    uint32_t flags;                  /**< [data node flags](@ref dnodeflags) */
    const struct lysc_node *schema;  /**< pointer to the schema definition of this node */
    struct lyd_node_inner *parent;   /**< pointer to the parent node, NULL in case of root node */
    struct lyd_node *next;           /**< pointer to the next sibling node (NULL if there is no one) */
    struct lyd_node *prev;           /**< pointer to the previous sibling node \note Note that this pointer is
                                          never NULL. If there is no sibling node, pointer points to the node
                                          itself. In case of the first node, this pointer points to the last
                                          node in the list. */
    struct lyd_meta *meta;           /**< pointer to the list of attributes of this node */

    union lyd_any_value {
        struct lyd_node *tree;       /**< data tree */
        const char *str;             /**< Generic string data */
        const char *xml;             /**< Serialized XML data */
        const char *json;            /**< I-JSON encoded string */
        char *mem;                   /**< LYD_ANYDATA_LYB memory chunk */
    } value;                         /**< pointer to the stored value representation of the anydata/anyxml node */
    LYD_ANYDATA_VALUETYPE value_type;/**< type of the data stored as lyd_node_any::value */
    ...;
};

typedef enum {
    LY_PREF_SCHEMA,          /**< value prefixes map to YANG import prefixes */
    LY_PREF_SCHEMA_RESOLVED, /**< value prefixes map to module structures directly */
    LY_PREF_XML,             /**< value prefixes map to XML namespace prefixes */
    LY_PREF_JSON             /**< value prefixes map to module names */
} LY_PREFIX_FORMAT;

struct ly_opaq_name {
    const char *name;             /**< node name, without prefix if any was defined */
    const char *prefix;           /**< identifier used in the qualified name as the prefix, can be NULL */
    union {
        const char *module_ns;    /**< format ::LY_PREF_XML - XML namespace of the node element */
        const char *module_name;  /**< format ::LY_PREF_JSON - (inherited) name of the module of the element */
    };
};

struct lyd_node_opaq {
    union {
        struct lyd_node node;               /**< implicit cast for the members compatible with ::lyd_node */
        struct {
            uint32_t hash;                  /**< always 0 */
            uint32_t flags;                 /**< always 0 */
            const struct lysc_node *schema; /**< always NULL */
            struct lyd_node_inner *parent;  /**< pointer to the parent node, NULL in case of root node */
            struct lyd_node *next;          /**< pointer to the next sibling node (NULL if there is no one) */
            struct lyd_node *prev;          /**< pointer to the previous sibling node \note Note that this pointer is
                                                 never NULL. If there is no sibling node, pointer points to the node
                                                 itself. In case of the first node, this pointer points to the last
                                                 node in the list. */
            struct lyd_meta *meta;          /**< always NULL */
            void *priv;                     /**< private user data, not used by libyang */
        };
    };                                      /**< common part corresponding to ::lyd_node */

    struct lyd_node *child;         /**< pointer to the child node (compatible with ::lyd_node_inner) */

    struct ly_opaq_name name;       /**< node name with module information */
    const char *value;              /**< original value */
    LY_PREFIX_FORMAT format;        /**< format of the node and any prefixes, ::LY_PREF_XML or ::LY_PREF_JSON */
    void *val_prefix_data;          /**< format-specific prefix data */
    uint32_t hints;                 /**< additional information about from the data source, see the [hints list](@ref lydhints) */

    struct lyd_attr *attr;          /**< pointer to the list of generic attributes of this node */
    const struct ly_ctx *ctx;       /**< libyang context */
};

struct lyd_meta {
    struct lyd_node *parent;         /**< data node where the metadata is placed */
    struct lyd_meta *next;           /**< pointer to the next metadata of the same element */
    struct lysc_ext_instance *annotation; /**< pointer to the annotation's definition */
    const char *name;                /**< metadata name */
    struct lyd_value value;          /**< metadata value representation */
};

#define 	LYD_PRINT_KEEPEMPTYCONT ...
#define 	LYD_PRINT_WD_ALL ...
#define 	LYD_PRINT_WD_ALL_TAG ...
#define 	LYD_PRINT_WD_EXPLICIT ...
#define 	LYD_PRINT_WD_IMPL_TAG ...
#define 	LYD_PRINT_WD_MASK ...
#define 	LYD_PRINT_WD_TRIM ...
#define 	LYD_PRINT_WITHSIBLINGS ...

// libc
void free(void *);
