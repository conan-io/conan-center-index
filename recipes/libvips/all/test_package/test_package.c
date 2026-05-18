#include <vips/vips.h>

#include <stdio.h>

int main(int argc, char **argv) {
    printf("libvips version: %s\n", vips_version_string());
    return 0;
}
