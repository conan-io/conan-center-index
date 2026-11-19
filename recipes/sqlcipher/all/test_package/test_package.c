#include <stdio.h>
#include <stdlib.h>
#include "sqlcipher/sqlite3.h"

int main(void) {
    printf("SQLite version (%d): %s\n", sqlite3_libversion_number(), sqlite3_libversion());
    return EXIT_SUCCESS;
}
