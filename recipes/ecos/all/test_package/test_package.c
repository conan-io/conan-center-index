#include <ecos/ecos.h>

#include <stdio.h>

int main(void) {
    printf("ECOS version %s\n", ECOS_ver());
    return 0;
}
