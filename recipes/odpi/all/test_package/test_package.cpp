#include <cstdlib>
#include "dpi.h"

int main(void)
{

    dpiVersionInfo versionInfo;
    dpiContext_getClientVersion(NULL, &versionInfo);

    return EXIT_SUCCESS;
}
