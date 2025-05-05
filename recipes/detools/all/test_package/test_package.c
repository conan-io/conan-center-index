#include <stdlib.h>
#include "detools.h"

/* Helper functions. */
static int flash_read(void *arg_p, void *dst_p, uintptr_t src, size_t size)
{
    return (0);
}

static int flash_write(void *arg_p, uintptr_t dst, void *src_p, size_t size)
{
    return (0);
}

static int flash_erase(void *arg_p, uintptr_t addr, size_t size)
{
    return (0);
}

static int step_set(void *arg_p, int step)
{
    return (0);
}

static int step_get(void *arg_p, int *step_p)
{
    return (0);
}

static int serial_read(uint8_t *buf_p, size_t size)
{
    return (0);
}

static int verify_written_data(int to_size, uint32_t to_crc)
{
    return (0);
}

int main()
{
    struct detools_apply_patch_in_place_t apply_patch;
    uint8_t buf[256];
    int res;
    size_t patch_size = 512;

    /* Initialize the in-place apply patch object. */
    res = detools_apply_patch_in_place_init(&apply_patch,
                                            flash_read,
                                            flash_write,
                                            flash_erase,
                                            step_set,
                                            step_get,
                                            patch_size,
                                            NULL);

    if (res != 0) {
        return (res);
    }
}
