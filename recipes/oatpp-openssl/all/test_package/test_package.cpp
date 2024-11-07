#include <iostream>
#include "oatpp-openssl/Config.hpp"

int main() {
    std::shared_ptr<oatpp::openssl::Config> config = oatpp::openssl::Config::createShared();
    std::cout << "Test package successful\n";
    return 0;
}
