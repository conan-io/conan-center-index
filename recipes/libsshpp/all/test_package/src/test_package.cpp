#include <sshpp/sshpp.hpp>
#include <iostream>

int main() {
    std::cout << "libsshpp " << sshpp::Library::version_string() << std::endl;
    return 0;
}
