#include <stdlib.h>
#include "detools.h"

int main(int argc, const char *argv[])
{
    int res;

    if (argc != 4) {
        printf("Wrong number of arguments.\n");

        return EXIT_FAILURE;
    }

    res = detools_apply_patch_filenames(argv[1], argv[2], argv[3]);

    if (res == 2780) {
        return EXIT_SUCCESS;
    } else {
        return EXIT_FAILURE;
    }
}
