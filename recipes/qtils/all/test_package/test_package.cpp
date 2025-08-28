#include <qtils/hex.hpp>
#include <string>
#include <vector>
#include <iostream>
#include <span>
#include <fmt/format.h>

int main() {
    std::string test_str = "Hello Qtils!";
    std::vector<uint8_t> data(test_str.begin(), test_str.end());
    
    // Test hex formatting using span
    std::span<const uint8_t> input_span(data);
    qtils::Hex hex{input_span};
    std::cout << fmt::format("{}", hex) << std::endl;
    
    return 0;
}
