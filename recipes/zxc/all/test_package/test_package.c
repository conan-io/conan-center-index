#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <zxc.h>

int main(void) {
    uint64_t bound = zxc_compress_bound(1024);
    printf("ZXC version: %s\n", ZXC_LIB_VERSION_STR);
    printf("Compress bound for 1024 bytes: %llu\n",
           (unsigned long long)bound);
    return 0;
}
