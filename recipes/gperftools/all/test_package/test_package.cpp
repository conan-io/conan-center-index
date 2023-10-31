#include <gperftools/tcmalloc.h>

#include <cassert>
#include <cstdlib>
#include <iostream>

int main() {
    void *p = tc_malloc(100);
    tc_free(p);
    std::cout << TC_VERSION_STRING << std::endl;
    return p == 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
