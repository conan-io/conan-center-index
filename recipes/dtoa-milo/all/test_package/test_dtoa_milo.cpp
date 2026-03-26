// Minimal roundtrip test for dtoa-milo: convert double → string → double
#include <dtoa-milo/dtoa_milo.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>

static bool verify(double value) {
    char buffer[64];
    dtoa_milo(value, buffer);

    char *end = nullptr;
    double roundtrip = strtod(buffer, &end);
    if (end == buffer || *end != '\0') {
        fprintf(stderr, "FAIL: strtod did not consume full string for %.17g -> \"%s\"\n",
                value, buffer);
        return false;
    }
    if (roundtrip != value) {
        fprintf(stderr, "FAIL: roundtrip mismatch %.17g -> \"%s\" -> %.17g\n",
                value, buffer, roundtrip);
        return false;
    }
    return true;
}

int main() {
    const double cases[] = {
        0.0, 1.0, -1.0,
        0.1, 0.12, 0.123, 1.2345,
        1.0 / 3.0, 2.0 / 3.0,
        1e10, 1e-10, 1e100, 1e-100,
        std::numeric_limits<double>::max(),
        std::numeric_limits<double>::min(),
        std::numeric_limits<double>::denorm_min(),
        std::numeric_limits<double>::epsilon(),
    };
    int failures = 0;
    for (double v : cases) {
        if (!verify(v))
            ++failures;
    }
    if (failures) {
        fprintf(stderr, "%d test(s) FAILED\n", failures);
        return 1;
    }
    printf("dtoa-milo: all roundtrip tests passed\n");
    return 0;
}
