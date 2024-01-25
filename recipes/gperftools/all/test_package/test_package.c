#include <gperftools/tcmalloc.h>

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
    void *p = tc_malloc(100);
    tc_free(p);
    puts(tc_version(NULL, NULL, NULL));
    return p == 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
