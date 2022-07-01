#include <stdio.h>
#include "xf86drm.h"

int main()
{
    drmVersionPtr v = drmGetLibVersion(0);
    printf("drm version: %d.%d.%d\n", v->version_major, v->version_minor, v->version_patchlevel);
    drmFree(v);
    printf("drm available: %d\n", drmAvailable());
    return 0;
}
