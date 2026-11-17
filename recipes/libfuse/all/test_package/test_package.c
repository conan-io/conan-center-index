#include <fuse.h>
#include <stdio.h>

int main() {
#ifdef LIBFUSE_HEADER_ONLY
    /* Headers only: use the API's types and macros, but no library symbols */
    struct fuse_operations operations = {0};
    (void)operations;
    printf("libfuse headers, FUSE_VERSION %d\n", FUSE_VERSION);
#else
    fuse_get_context();
#endif
    return 0;
}
