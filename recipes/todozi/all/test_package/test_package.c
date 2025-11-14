#include "todozi.h"
#include <stdio.h>

int main() {
    // Test basic library loading and initialization
    todozi_todozi_t* instance = todozi_new();
    if (!instance) {
        printf("Failed to create todozi instance\n");
        return -1;
    }

    printf("Todozi library loaded and instance created successfully\n");

    // Clean up
    todozi_free(instance);

    printf("Test passed!\n");
    return 0;
}
