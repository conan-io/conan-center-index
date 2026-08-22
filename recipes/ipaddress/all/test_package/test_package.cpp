#include <cstdlib>
#include <iostream>
#include "ipaddress/ipaddress.hpp"


int main(void) {
    auto ip = ipaddress::ipv6_address::parse("fec0::1ff:fe23:4567:890a%eth2");
    std::cout << "Parsing ipv6: " << ip << std::endl;

    return EXIT_SUCCESS;
}
