#include <typecast.h>
#include <stdio.h>

int main(void) {
    /* Test version function */
    const char* version = typecast_version();
    printf("Typecast SDK version: %s\n", version);
    return 0;
}
