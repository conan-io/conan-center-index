#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

/*
 * psqlodbc ships loadable driver modules (psqlodbcw.so / psqlodbca.so) with
 * no public headers or link interface, so the smoke test dlopen()s the
 * module and resolves a known ODBC entry point instead of linking directly.
 */
int main(int argc, char **argv)
{
    void *handle = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    void *symbol = handle ? dlsym(handle, "SQLAllocHandle") : NULL;
    if (!symbol) {
        fprintf(stderr, "failed to load psqlodbc driver %s: %s\n", argv[1], dlerror());
        return EXIT_FAILURE;
    }

    printf("psqlodbc driver loaded: %s\n", argv[1]);
    dlclose(handle);
    return EXIT_SUCCESS;
}
