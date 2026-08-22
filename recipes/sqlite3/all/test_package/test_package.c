#include <stdio.h>
#include <sqlite3.h>

int main() {
    printf("SQLite Version: %s\n", sqlite3_libversion());
    return 0;
}
