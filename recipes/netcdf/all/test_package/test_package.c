#include "netcdf.h"
#include <stdio.h>

int main() {
    printf("netcdf version: %s\n", nc_inq_libvers());
    return 0;
}
