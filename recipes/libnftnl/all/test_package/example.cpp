#include <iostream>
#include <cstdlib>
#include <libnftnl/table.h>

int main() {
    struct nftnl_table *nt = nftnl_table_alloc();
    nftnl_table_free(nt);

    return EXIT_SUCCESS;
}