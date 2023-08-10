#include <sqlite3.h>
#include <spatialite.h>

#include <stdio.h>

int main(void) {
    printf("libspatialite info:\n");
    printf("-- version: %s\n", spatialite_version());
    printf("-- target cpu: %s\n", spatialite_target_cpu());
    spatialite_initialize();
    spatialite_shutdown();
    return 0;
}
