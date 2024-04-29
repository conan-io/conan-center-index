#include <stdio.h>
#include <string.h>
#include <hb.h>

int main() {
    const char *version = hb_version_string();
    printf("harfbuzz version: %s", version);
    return;
}