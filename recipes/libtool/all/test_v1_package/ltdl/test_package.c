#include "ltdl.h"

#include <stdio.h>
#include <stdlib.h>

typedef int (*liba_func_t)(int);

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "Need an argument\n");
        return EXIT_FAILURE;
    }
    const char* libname = argv[1];
    lt_dlinit();

    fprintf(stderr, "lt_dlopenext(\"%s\")\n", libname);
    lt_dlhandle ltdl_liba = lt_dlopenext(libname);
    if (!ltdl_liba) {
        fprintf(stderr, "lt_dlopenext failed.\n");
        return EXIT_FAILURE;
    }

    liba_func_t liba_func = (liba_func_t) lt_dlsym(ltdl_liba, "liba_function");
    int res = liba_func(21);
    printf("Result is %d\n", res);
    if (res != 42) {
        fprintf(stderr, "Result is incorrect\n");
        return EXIT_FAILURE;
    }

    lt_dlclose(ltdl_liba);

    lt_dlexit();
    return EXIT_SUCCESS;
}
