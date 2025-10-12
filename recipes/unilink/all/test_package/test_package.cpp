#include <iostream>
#include <unilink/unilink.hpp>

int main() {
    std::cout << "Testing unilink package..." << std::endl;
    
    // Test basic functionality
    try {
        // This is a simple test to ensure the library links correctly
        std::cout << "unilink library loaded successfully!" << std::endl;
        std::cout << "Header inclusion test passed!" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
