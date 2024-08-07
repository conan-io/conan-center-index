#include <libmount/libmount.h>

#include <stdio.h>
#include <stdlib.h>

int main()
{
    struct libmnt_context *ctx = mnt_new_context();
    if (!ctx) {
        printf("failed to initialize libmount\n");
        return EXIT_FAILURE;
    }
    printf("path to fstab: %s", mnt_get_fstab_path());
    mnt_free_context(ctx);
    return EXIT_SUCCESS;
}
