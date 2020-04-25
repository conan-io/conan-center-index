#include "apu_version.h"

#include <stdio.h>

int main() {
    printf("apr-util version %s\n", apu_version_string());
    return 0;
}
