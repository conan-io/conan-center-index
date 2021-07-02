#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>

#ifdef USE_EMPTY_VFS
#define DB_NAME ":memory:"
#else
#define DB_NAME "bincrafters.db"
#endif

int main() {
    sqlite3* db_instance = NULL;
    char* errmsg = NULL;
    int result = 0;

    printf("SQLite Version: %s\n", sqlite3_libversion());

    printf("Creating new data base ...\n");
    result = sqlite3_open(DB_NAME, &db_instance);
    if (result != SQLITE_OK) {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db_instance));
        sqlite3_close(db_instance);
        return EXIT_FAILURE;
    }
    printf("Done!\n");

    printf("Creating new table...\n");
    result = sqlite3_exec(db_instance, "CREATE TABLE package(ID INT PRIMARY KEY NOT NULL);", NULL, 0, &errmsg);
    if(result != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", errmsg);
        sqlite3_free(errmsg);
        return EXIT_FAILURE;
    }
    printf("Done!\n");

    printf("Closing connection ...\n");
    sqlite3_close(db_instance);
    if(result != SQLITE_OK) {
        fprintf(stderr, "Connection error: %s\n", errmsg);
        sqlite3_free(errmsg);
        return EXIT_FAILURE;
    }
    printf("Done!\n");

    return EXIT_SUCCESS;
}
