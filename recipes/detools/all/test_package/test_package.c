#include <stdlib.h>
#include "detools.h"

#define EXPECTED_PATCHED_FILE_SIZE 2780

int main(int argc, const char *argv[])
{
    int res;

    if (argc != 4) {
        printf("Wrong number of arguments.\n");

        return EXIT_FAILURE;
    }

    res = detools_apply_patch_filenames(argv[1], argv[2], argv[3]);

    if (res == EXPECTED_PATCHED_FILE_SIZE) {
        return EXIT_SUCCESS;
    } else {
        return EXIT_FAILURE;
    }
}
