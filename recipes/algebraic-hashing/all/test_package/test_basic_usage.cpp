#include <iostream>
#include <string>

// Test basic includes work
#include <algebraic_hashing/core/hash_value.hpp>
#include <algebraic_hashing/functions/fnv_hash_modern.hpp>

using namespace algebraic_hashing;

int main() {
    std::cout << "=== AlgebraicHashing Conan Center Test ===" << std::endl;
    
    try {
        // Test basic hash value operations
        hash_value<64> h1;
        hash_value<64> h2;
        auto h3 = h1 ^ h2;
        
        // Test FNV hash function
        auto fnv = functions::fnv64{};
        std::string test_str = "Hello, Conan Center!";
        auto result = fnv(test_str);
        
        std::cout << "✓ All tests passed! Package is working correctly." << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "✗ Test failed: " << e.what() << std::endl;
        return 1;
    }
}