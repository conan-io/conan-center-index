/* Exercises the WINAPI/stdcall variant (zlibwapi.dll).
   ZLIB_WINAPI must be defined before the headers, so that the declarations use the
   same (stdcall) calling convention the zlibwapi library was built with. The recipe
   propagates it through the zlibwapi component, so this file must not define it
   itself: that is exactly what is being tested here. */
#include <stdio.h>
#include <stdlib.h>

#ifndef ZLIB_WINAPI
#error "ZLIB_WINAPI is not defined: the zlibwapi component does not propagate it"
#endif

#include <zlib.h>
#include <unzip.h>
#include <zip.h>

#define ARCHIVE "test_package_wapi.zip"

int main(void) {
    static const char content[] = "hello zlibwapi";
    zipFile zf;
    unzFile uf;

    printf("ZLIBWAPI VERSION: %s\n", zlibVersion());

    /* Unlike the regular zlib DLL, zlibwapi.dll also exports contrib/minizip */
    zf = zipOpen(ARCHIVE, APPEND_STATUS_CREATE);
    if (zf == NULL) {
        fprintf(stderr, "zipOpen failed\n");
        return EXIT_FAILURE;
    }
    if (zipOpenNewFileInZip(zf, "hello.txt", NULL, NULL, 0, NULL, 0, NULL,
                            Z_DEFLATED, Z_DEFAULT_COMPRESSION) != ZIP_OK) {
        fprintf(stderr, "zipOpenNewFileInZip failed\n");
        return EXIT_FAILURE;
    }
    if (zipWriteInFileInZip(zf, content, (unsigned)sizeof(content) - 1) != ZIP_OK) {
        fprintf(stderr, "zipWriteInFileInZip failed\n");
        return EXIT_FAILURE;
    }
    zipCloseFileInZip(zf);
    zipClose(zf, NULL);

    uf = unzOpen(ARCHIVE);
    if (uf == NULL) {
        fprintf(stderr, "unzOpen failed\n");
        return EXIT_FAILURE;
    }
    if (unzLocateFile(uf, "hello.txt", 0) != UNZ_OK) {
        fprintf(stderr, "unzLocateFile failed\n");
        return EXIT_FAILURE;
    }
    unzClose(uf);
    remove(ARCHIVE);

    printf("ZLIBWAPI MINIZIP ROUND TRIP OK\n");
    return EXIT_SUCCESS;
}
