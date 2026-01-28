#include <sockpp/socket.h>
#include <sockpp/version.h>
#include <iostream>

int main() {
    std::cout << "Testing sockpp library..." << std::endl;
    
    // Initialize sockpp library
    sockpp::socket_initializer::initialize();
    
    // Test version info
    std::cout << "sockpp version: " << sockpp::SOCKPP_VERSION << std::endl;
    
    // Test socket creation (without connecting)
    try {
        sockpp::socket sock;
        std::cout << "Socket created successfully" << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "sockpp test passed!" << std::endl;
    return 0;
}
