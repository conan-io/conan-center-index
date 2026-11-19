#include "Poco/JWT/Signer.h"
#include <iostream>


int main() {
    Poco::JWT::Signer signer("Conan");
    std::cout << "Poco JWT: " << signer.getHMACKey() << std::endl;
    return 0;
}
