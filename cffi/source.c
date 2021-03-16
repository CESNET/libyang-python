/**
 * Copyright (c) 2020 CESNET, z.s.p.o.
 * SPDX-License-Identifier: MIT
 * Author David Sedlák
*/

#include <libyang/libyang.h>

int get_array_size(void *array) {
    if(!array) {
        return 0;
    }

    return LY_ARRAY_COUNT(array);
}

const char *lyd_data_canonic(struct lyd_node_term *node) {
    return LYD_CANON_VALUE(node);
}
