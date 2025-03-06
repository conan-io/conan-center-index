#include <iostream>
#include <cstdlib>
#include <libnetfilter_log/libnetfilter_log.h>

int main() {
    struct nflog_handle *nl = nflog_open();
    if (nl == NULL) {
        std::cerr << "nflog_open\n";
        return EXIT_FAILURE;
    }
    nflog_close(nl);

    return EXIT_SUCCESS;
}