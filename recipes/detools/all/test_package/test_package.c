#include <stdlib.h>
#include "detools.h"

static int dummy_function()
{
    return (0);
}

int main()
{
    struct detools_apply_patch_in_place_t apply_patch;
    uint8_t buf[256];
    int res;
    size_t patch_size = 512;

    res = detools_apply_patch_in_place_init(&apply_patch,
                                            dummy_function,
                                            dummy_function,
                                            dummy_function,
                                            dummy_function,
                                            dummy_function,
                                            patch_size,
                                            NULL);
    printf("detools_apply_patch_in_place_init: %d\n", res);
    if (res != 0) {
        return (res);
    }
}
