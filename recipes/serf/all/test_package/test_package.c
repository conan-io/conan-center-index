#include "serf.h"

#include <stdio.h>

int main() {
    int major, minor, patch;
    serf_lib_version(&major, &minor, &patch);
    printf("serf version %d.%d.%d\n", major, minor, patch);
    return 0;
}
