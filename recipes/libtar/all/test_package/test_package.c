#include <libtar.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#if defined(_MSC_VER)
# include <io.h>
#else
# include <fcntl.h>
#endif

int main(int argc, const char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Need one argument\n");
        return 1;
    }
    TAR *handle;
    tartype_t *type = NULL;
    const int oflags = O_RDONLY;
    const int mode = 0755;
    const int options = TAR_GNU | TAR_VERBOSE | TAR_CHECK_MAGIC;
    if (tar_open(&handle, argv[1], type, oflags, mode, options) < 0) {
        fprintf(stderr, "tar_open failed: errno = %d\n", errno);
        return 1;
    }
    if (th_read(handle) < 0) {
        fprintf(stderr, "th_read failed\n");
        return 1;
    }
    if (tar_extract_file(handle, "hello_world") < 0) {
        fprintf(stderr, "tar_extract failed\n");
        return 1;
    }
    if (tar_close(handle) < 0) {
        fprintf(stderr, "tar_close failed\n");
        return 1;
    }
    return 0;
}
