#include <db.h>

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    DB *dbp;
    int res;
    res = db_create(&dbp, NULL, 0);
    if (res != 0) {
        puts("db_create failed\n");
        return EXIT_FAILURE;
    }

    res = dbp->close(dbp, 0);
    if (res != 0) {
        puts("DP->close failed\n");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
