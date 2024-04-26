#include <stdio.h>
#include <string.h>
#include <hb.h>

int main() {
    const char *my_string = "my-string";
    size_t length = strlen(my_string);

    hb_blob_t* blob = hb_blob_create(my_string, length, HB_MEMORY_MODE_READONLY, NULL, NULL);

    return 0;
}
