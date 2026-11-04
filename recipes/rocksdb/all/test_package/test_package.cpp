#include <cstdlib>
#include "rocksdb/db.h"
#include "rocksdb/c.h"


int main() {
    rocksdb_options_t *options = rocksdb_options_create();
    rocksdb_free(options);

    return EXIT_SUCCESS;
}
