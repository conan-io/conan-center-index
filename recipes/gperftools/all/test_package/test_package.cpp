#include <gperftools/tcmalloc.h>

#include <cassert>
#include <cstdlib>
#include <iostream>

int main() {
    void *p = tc_malloc(100);
    assert(p != nullptr);
    tc_free(p);
    std::cout << TC_VERSION_STRING << std::endl;
    return EXIT_SUCCESS;
}
