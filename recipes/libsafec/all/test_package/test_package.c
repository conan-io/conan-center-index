#include <safe_str_lib.h>
#include <stdlib.h>

void
constraint_handler(const char* msg, void* ptr, errno_t error)
{
    printf("Constraint handler: %s\n", msg);
    printf("Success!\n");
    exit(0);
}

int
main(int argc, char** argv)
{
    char dst[2];

    set_str_constraint_handler_s(constraint_handler);

    strcpy_s(dst, sizeof dst, "Too long!");
    printf("Fail!\n");

    return 1;
}
