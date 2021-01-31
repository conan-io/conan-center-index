#include <libsafec/safe_str_lib.h>

void
constraint_handler(const char* msg, void* ptr, errno_t error)
{
    printf("Constraint handler: %s\n", msg);
}

int
main(int argc, char** argv)
{
    char dst[2];

    set_str_constraint_handler_s(constraint_handler);

    int r = strcpy_s(dst, sizeof dst, "Too long!");
    if (r == ESNOSPC)
        printf("Success!\n");

    return 0;
}
