#include <gperftools/tcmalloc.h>

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
    void *p = tc_malloc(100);
    tc_free(p);
    puts(TC_VERSION_STRING);
    return p == 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
