#include "X11/xshmfence.h"

int main() {
    int		        fd;
    struct xshmfence    *x;

    fd = xshmfence_alloc_shm();
    if (fd < 0) {
        return 1;
    }


    x = xshmfence_map_shm(fd);
    if (!x) {
        return 1;
    }

    xshmfence_unmap_shm(x);

    return 0;
}
