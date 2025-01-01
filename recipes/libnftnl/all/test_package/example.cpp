#include <iostream>
#include <cstdlib>
#include <libnftnl/table.h>

int main() {
    struct nftnl_table *nt = nftnl_table_alloc();
    if (nt == NULL) {
        std::cerr << "nftnl_table_alloc\n";
        return EXIT_FAILURE;
    }
    nftnl_table_free(nt);

    return EXIT_SUCCESS;
}