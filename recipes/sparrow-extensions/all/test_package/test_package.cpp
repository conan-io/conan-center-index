#include <sparrow_extensions/uuid_array.hpp>
#include <sparrow_extensions/json_array.hpp>
#include <sparrow_extensions/bool8_array.hpp>
#include <sparrow_extensions/config/sparrow_extensions_version.hpp>

#include <iostream>
#include <vector>
#include <array>

int main() {
    std::cout << "sparrow-extensions version: "
              << sparrow_extensions::SPARROW_EXTENSIONS_VERSION_MAJOR << "."
              << sparrow_extensions::SPARROW_EXTENSIONS_VERSION_MINOR << "."
              << sparrow_extensions::SPARROW_EXTENSIONS_VERSION_PATCH << std::endl;

    // Test uuid_array
    {
        std::array<sparrow::byte_t, 16> uuid{};
        for (size_t i = 0; i < 16; ++i) {
            uuid[i] = static_cast<sparrow::byte_t>(i);
        }
        std::vector<std::array<sparrow::byte_t, 16>> uuids = {uuid};
        sparrow_extensions::uuid_array arr(uuids);
        std::cout << "uuid_array size: " << arr.size() << std::endl;
    }

    // Test json_array
    {
        std::vector<std::string> json_values = {R"({"test": true})"};
        sparrow_extensions::json_array arr(json_values);
        std::cout << "json_array size: " << arr.size() << std::endl;
    }

    // Test bool8_array
    {
        std::vector<bool> bool_values = {true, false, true};
        sparrow_extensions::bool8_array arr(bool_values);
        std::cout << "bool8_array size: " << arr.size() << std::endl;
    }

    std::cout << "All tests passed!" << std::endl;
    return 0;
}
