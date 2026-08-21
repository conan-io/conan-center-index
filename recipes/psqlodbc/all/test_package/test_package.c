#include <stdio.h>
#include <stdlib.h>

#include <dlfcn.h>

/*
 * psqlodbc ships ODBC driver modules (psqlodbcw.so / psqlodbca.so) that are
 * loaded at runtime by the unixODBC driver manager via dlopen(). They expose
 * no public headers and no link interface, so the smoke test simply loads the
 * module by path and resolves a known ODBC entry point (matching the upstream
 * "^SQL" export regex). No PostgreSQL server or DSN is required.
 */
int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s <psqlodbc module path>\n", argv[0]);
        return EXIT_FAILURE;
    }

    void *handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        fprintf(stderr, "dlopen(%s) failed: %s\n", argv[1], dlerror());
        return EXIT_FAILURE;
    }

    dlerror();
    void *symbol = dlsym(handle, "SQLAllocHandle");
    const char *error = dlerror();
    if (error || !symbol) {
        fprintf(stderr, "dlsym(SQLAllocHandle) failed: %s\n",
                error ? error : "symbol is NULL");
        dlclose(handle);
        return EXIT_FAILURE;
    }

    printf("psqlodbc driver loaded: %s\n", argv[1]);
    dlclose(handle);
    return EXIT_SUCCESS;
}
