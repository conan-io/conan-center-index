#include <stdio.h>
#include <grib_api.h>

int main() {
    long version = grib_get_api_version();
    printf("ecCodes version: %ld\n", version);
    return 0;
}
