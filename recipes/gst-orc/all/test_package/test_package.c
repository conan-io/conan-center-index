#include <orc/orc.h>

#include <stdio.h>

int main() {
    orc_init();
    printf("ORC library version: %s\n", orc_version_string());
}
