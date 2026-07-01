// Minimal compile + version check for OTL.
// OTL requires a database-type macro (OTL_ODBC, OTL_ORA8, etc.) to enable
// actual database classes. For this test we just verify the header is
// includable and the version macro is defined.
#if defined(_WIN32)
#  define OTL_ODBC  // ODBC headers available natively on Windows
#endif
#include <otl/otlv4.h>
#include <cstdio>

int main() {
    printf("OTL version: 0x%06lX\n", (long)OTL_VERSION_NUMBER);

#if !defined(OTL_VERSION_NUMBER)
    fprintf(stderr, "OTL_VERSION_NUMBER not defined\n");
    return 1;
#endif

    // Verify the version macro is a reasonable value (>= 4.0.0 = 0x040000)
    if (OTL_VERSION_NUMBER < 0x040000L) {
        fprintf(stderr, "Unexpected OTL_VERSION_NUMBER: 0x%06lX\n",
                (long)OTL_VERSION_NUMBER);
        return 1;
    }

    printf("otl: version check passed\n");
    return 0;
}
