#include <stdio.h>
#include <stdlib.h>

#include <sys/capability.h>

int main(void) {
    puts("Allocate cap state");
    cap_t cap = cap_get_proc();
    if (!cap) {
        puts("Failed");
        return EXIT_FAILURE;
    }
    puts("Success");
    cap_free(cap);
}
