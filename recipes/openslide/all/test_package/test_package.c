#include <openslide.h>
#include <stdio.h>

int main() {
    printf("OpenSlide version: %s\n", openslide_get_version());
    return 0;
}
