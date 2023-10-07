#include "iowow/iwkv.h"

int main() {
    IWKV_OPTS opts = {
        .path   = "example1.db",
        .oflags = IWKV_TRUNC  // Cleanup database before open
    };
    IWKV iwkv;
    iwrc rc = iwkv_open(&opts, &iwkv);

    iwkv_close(&iwkv);

    return 0;
}
