#include <magic.h>

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    const char *magic_full;
    magic_t magic_cookie;

    magic_cookie = magic_open(MAGIC_MIME);

    if (magic_cookie == NULL) {
        printf("unable to initialize magic library\n");
        return 1;
    }

    char *mgc_path = getenv("MAGIC");
    printf("Loading default magic database from %s\n", mgc_path);

    if (magic_load(magic_cookie, NULL) != 0) {
        printf("cannot load magic database - %s\n", magic_error(magic_cookie));
        magic_close(magic_cookie);
        return 1;
    }

    magic_full = magic_file(magic_cookie, argv[0]);
    printf("%s\n", magic_full);
    magic_close(magic_cookie);
    return 0;
}
