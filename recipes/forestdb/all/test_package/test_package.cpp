#include <iostream>
#include <libforestdb/forestdb.h>

int main(void) {
    auto fdb_config = fdb_get_default_config();
    auto const fdb_status = fdb_init(&fdb_config);
    if (FDB_RESULT_SUCCESS != fdb_status) exit(-1);
    return 0;
}
