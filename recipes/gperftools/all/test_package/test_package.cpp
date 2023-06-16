#include <gperftools/tcmalloc.h>

#include <cstdlib>
#include <iostream>

int main() {
    void *p = tc_malloc(100);
    tc_free(p);
    std::cout << TC_VERSION_STRING << std::endl;
    return EXIT_SUCCESS;
}
