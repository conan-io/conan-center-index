/* example was taken from https://www.gnu.org/ghm/2011/paris/slides/andreas-enge-mpc.pdf */

#include <cdi_core_api.h>
#include <cdi_logger_api.h>
#include <stdlib.h>

int main () {
    CdiLoggerInitialize(); // Intialize logger so we can use the CDI_LOG_THREAD() macro to generate console messages.

    CDI_LOG_THREAD(kLogInfo, "CDI SDK Version: %d.%d.%d\n", CDI_SDK_VERSION, CDI_SDK_MAJOR_VERSION,
                   CDI_SDK_MINOR_VERSION);

    CdiLoggerShutdown(false);

    return EXIT_SUCCESS;
}
