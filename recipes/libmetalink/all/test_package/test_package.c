#include <metalink/metalink.h>

#include <stdio.h>

int main(void) {
    int major, minor, patch;
    metalink_get_version(&major, &minor, &patch);
    printf("libmetalink version %i.%i.%i\n", major, minor, patch);
    return 0;
}
