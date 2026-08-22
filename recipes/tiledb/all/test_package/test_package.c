#include <tiledb/tiledb.h>

#include <stdio.h>

int main() {
  tiledb_ctx_t* ctx;
  tiledb_ctx_alloc(NULL, &ctx);
  tiledb_ctx_free(&ctx);

  int32_t major, minor, rev;
  tiledb_version(&major, &minor, &rev);
  printf("TileDB version: %d.%d.%d\n", major, minor, rev);

  return 0;
}
