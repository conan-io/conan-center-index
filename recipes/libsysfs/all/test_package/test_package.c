#include <stdio.h>
#include <stdlib.h>

#include <sysfs/libsysfs.h>

int main(void) {
    char sysfs_mntpath[SYSFS_PATH_MAX];
    int rc = sysfs_get_mnt_path(sysfs_mntpath, SYSFS_PATH_MAX);
    if (rc < 0) {
        puts("Failed");
        return EXIT_FAILURE;
    }
    puts("Success");
    return EXIT_SUCCESS;
}
