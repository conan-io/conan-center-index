#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
    void *p = malloc(100);
    free(p);
    return p == 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
