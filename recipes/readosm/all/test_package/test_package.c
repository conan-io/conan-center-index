# include <readosm.h>

#include <stdio.h>

int main(void) {
    printf("readosm %s built with:\n", readosm_version());
    printf("-- expat %s\n", readosm_expat_version());
    printf("-- zlib %s\n", readosm_zlib_version());
    return 0;
}
