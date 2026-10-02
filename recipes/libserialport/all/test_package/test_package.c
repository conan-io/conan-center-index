#include <libserialport.h>
#include <stdio.h>

int main(void) {
    printf("libserialport version: %s\n", sp_get_lib_version_string());
    return 0;
}
