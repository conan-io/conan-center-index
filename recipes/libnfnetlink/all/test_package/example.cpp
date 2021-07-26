#include <iostream>
#include <cstdlib>
#include <libnfnetlink/libnfnetlink.h>

int main() {
    struct nfnl_handle *nl = nfnl_open();
    if (nl == NULL) {
        std::cerr << "nfnl_open\n";
        return EXIT_FAILURE;
    }
    nfnl_close(nl);

    return EXIT_SUCCESS;
}
