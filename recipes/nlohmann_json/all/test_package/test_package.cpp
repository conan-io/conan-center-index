#include <iostream>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
    const json data = {
        {"pi", 3.141},
        {"happy", true},
        {"name", "Niels"},
        {"nothing", nullptr},
        {"answer", {
            {"everything", 42}
        }},
        {"list", {1, 0, 2}},
        {"object", {
            {"currency", "USD"},
            {"value", 42.99}
        }}
    };

    std::cout << data.dump(4) << std::endl;
    return 0;
}
