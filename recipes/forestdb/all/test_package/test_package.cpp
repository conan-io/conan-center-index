#include <cstdlib>
#include <iostream>
#include <libforestdb/forestdb.h>

int main(void) {
    fdb_config default_config = fdb_get_default_config();
    fdb_status const status = fdb_init(&default_config);
    if (FDB_RESULT_SUCCESS != status) return -1;
    return 0;
}
