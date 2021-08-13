#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <minizip/zip.h>
#include <minizip/unzip.h>
#ifdef _WIN32
    #include <minizip/iowin32.h>
#endif

#include <minizip/mztools.h>

const char text[] = "Conveying or northward offending admitting perfectly my.";
const char* zip_fname = "test_minizip.zip";

int main(int argc, char** argv) {
    zipFile zf = zipOpen64(zip_fname, APPEND_STATUS_CREATE);
    if (zf == NULL) {
        printf("Error in zipOpen64, fname: %s\n", zip_fname);
        exit(EXIT_FAILURE);
    }

    int res;
    zip_fileinfo zfi = {0};
    res = zipOpenNewFileInZip64(zf, "fname.bin", &zfi, NULL, 0, NULL, 0, NULL, Z_DEFLATED, Z_BEST_COMPRESSION, 0);
    if (res != ZIP_OK) {
        printf("Error in zipOpenNewFileInZip64, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = zipWriteInFileInZip(zf, text, sizeof(text));
    if (res != ZIP_OK) {
        printf("Error in zipWriteInFileInZip, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = zipCloseFileInZip(zf);
    if (res != ZIP_OK) {
        printf("Error in zipCloseFileInZip, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    res = zipClose(zf, "Test MiniZip");
    if(res != ZIP_OK) {
        printf("Error in zipClose, code: %d\n", res);
        exit(EXIT_FAILURE);
    }

    printf("ZIP file created, name: %s\n", zip_fname);

    return EXIT_SUCCESS;
}

