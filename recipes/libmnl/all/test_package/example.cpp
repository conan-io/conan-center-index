#include <iostream>
#include <cstdlib>
#include <libmnl/libmnl.h>

int main() {
    struct mnl_socket *nl = mnl_socket_open(NETLINK_NETFILTER);
    if (nl == NULL) {
        std::cerr << "mnl_socket_open\n";
        return EXIT_FAILURE;
    }
    mnl_socket_close(nl);

    return EXIT_SUCCESS;
}
