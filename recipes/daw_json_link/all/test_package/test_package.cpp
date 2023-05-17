#include <iostream>
#include <string>

#include "daw/json/daw_json_link.h"

int main() {
    std::string json_data = "[1, 2, 3, 4, 5]";

    auto const obj = daw::json::from_json_array<int>(json_data);

    for (auto val : obj) {
        std::cout << val << std::endl;
    }

    return 0;
}
