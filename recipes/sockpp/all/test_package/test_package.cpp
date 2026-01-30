#include <sockpp/socket.h>
#include <sockpp/version.h>
#include <sockpp/inet_address.h>
#include <iostream>

int main() {
    sockpp::inet_address address(0x7f000001, 0);
    std::cout << "sockpp test passed!" << std::endl;
    return 0;
}
