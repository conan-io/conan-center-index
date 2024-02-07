#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
    void *p = malloc(100);
    printf("%p\n", p);    
    free(p);
    return p == 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
