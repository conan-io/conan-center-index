#include <gdbm.h>

#include <stdlib.h>
#include <string.h>
#include <fcntl.h>

#define SET_DATUM_CSTR(DATUM, CSTR) do {(DATUM).dptr=(CSTR); (DATUM).dsize=strlen(CSTR)+1;} while (0)

int main(int argc, char *argv[]) {
    GDBM_FILE file;
    int res;
    gdbm_count_t count;
    datum key, content, fetch;

    file = gdbm_open("test.db", 512, GDBM_WRCREAT, 0644, NULL);
    if (file == NULL) {
        puts("gdbm_open failed\n");
        return EXIT_FAILURE;
    }

    res = gdbm_count(file, &count);
    if (res != 0) {
        puts("gdbm_count failed\n");
        return EXIT_FAILURE;
    }

    SET_DATUM_CSTR(key, "key");
    SET_DATUM_CSTR(content, "content");
    res = gdbm_store(file, key, content, GDBM_INSERT);
    if (res != 0) {
        puts("gdbm_store failed\n");
        return EXIT_FAILURE;
    }

    if (!gdbm_exists(file, key)) {
        puts("gdbm_exists failed: cannot find key");
        return EXIT_FAILURE;
    }

    memset(&fetch, 0, sizeof(fetch));
    fetch = gdbm_fetch(file, key);
    if (content.dsize != fetch.dsize) {
        puts("gdbm_fetch failed: dsize does not match\n");
    }
    if (strncmp(content.dptr, fetch.dptr, strlen(content.dptr))) {
        puts("gdbm_fetch failed: dptr does not match\n");
    }

    res = gdbm_close(file);
    if (res != 0) {
        puts("gdbm_close failed\n");
        return EXIT_FAILURE;
    }

    if (gdbm_errno) {
        puts("gdbm_errno nonzero\n");
        puts(gdbm_strerror(gdbm_errno));
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
