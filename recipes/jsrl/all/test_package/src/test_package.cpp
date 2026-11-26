#include <jsrl/jsrl.hpp>
#include <iostream>
#include <sstream>

// Basic test that verifies the jsrl library can be linked
// and headers are accessible. Tests basic parse and access operations.

int main() {
    try {
        // Test 1: Parse a simple JSON object
        std::cout << "Test 1: Parsing simple JSON..." << std::endl;
        std::istringstream iss(R"({"name": "test", "value": 42, "active": true})");
        jsrl::Json json;
        iss >> json;

        // Test 2: Verify we can access the parsed data
        std::cout << "Test 2: Accessing parsed data..." << std::endl;
        if (!json.is_object()) {
            std::cerr << "ERROR: Expected object type" << std::endl;
            return 1;
        }

        std::string name = json["name"].as_string();
        if (name != "test") {
            std::cerr << "ERROR: Expected name='test', got '" << name << "'" << std::endl;
            return 1;
        }

        long long value = json["value"].as_number_sint();
        if (value != 42) {
            std::cerr << "ERROR: Expected value=42, got " << value << std::endl;
            return 1;
        }

        bool active = json["active"].as_bool();
        if (!active) {
            std::cerr << "ERROR: Expected active=true" << std::endl;
            return 1;
        }

        std::cout << "\nAll tests passed!" << std::endl;
        std::cout << "JSRL library test successful!" << std::endl;
        return 0;

    } catch (jsrl::Json::Error const& e) {
        std::cerr << "ERROR: JSRL exception: " << e.what() << std::endl;
        return 1;
    } catch (std::exception const& e) {
        std::cerr << "ERROR: Exception: " << e.what() << std::endl;
        return 1;
    }
}
