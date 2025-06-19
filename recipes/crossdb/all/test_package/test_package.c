#include <stdio.h>
#include <stdlib.h>

#include <crossdb.h>

int main () {
    printf("Cross DB Version: %s\n", xdb_version());
    return EXIT_SUCCESS;
}
