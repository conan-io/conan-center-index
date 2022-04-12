#include <stdio.h>
#include "dr_flac.h"

int main(void) {
    const char *version = drflac_version_string();
    printf("dr_flac version: %s\n", version);

    return 0;
}
