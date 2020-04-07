#include <iostream>
#include "xf86drm.h"

int main()
{
    drmVersionPtr v = drmGetLibVersion(0);
    std::cout << "drm version: " << v->version_major << '.' << v->version_minor << '.' << v->version_patchlevel << std::endl;
    drmFree(v);
    std::cout << "drm available: " << drmAvailable() << std::endl;
    return 0;
}
