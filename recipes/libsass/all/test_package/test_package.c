#include <sass.h>

#include <stdio.h>

int main() {
    printf("libsass version %s\t language version %s\n", libsass_version(), libsass_language_version());
    return 0;
}
