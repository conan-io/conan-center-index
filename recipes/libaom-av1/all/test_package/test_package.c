#include "aom/aom_codec.h"
#include <stdio.h>

int main() {
    printf("Version: %s\n", aom_codec_version_str());
    return 0;
}
