#include <stdlib.h>
#include <stdio.h>
#include "rocksdb/c.h"

int main() {
  rocksdb_options_t *options = rocksdb_options_create();
  rocksdb_options_set_create_if_missing(options, 1);
  char* err = NULL;
  rocksdb_t* db = rocksdb_open(options, "testdb_stable", &err);

  if (!db) {
    printf("DB error: %s\n", err);
  } else {
    rocksdb_close(db);
  }

  if(err) {
    rocksdb_free(err);
  }

  if(options) {
    rocksdb_free(options);
  }

  return EXIT_SUCCESS;
}
