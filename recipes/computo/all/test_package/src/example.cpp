#include <computo.hpp>
#include <iostream>

int main() {
    // Simple test of the computo library
    // Use the json type from computo.hpp which re-exports nlohmann::json
    auto script = nlohmann::json::array({"+", 2, 3});
    auto input = nlohmann::json::object();
    
    try {
        auto result = computo::execute(script, input);
        std::cout << "Test passed: 2 + 3 = " << result << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}