#include <RichJson.hpp>

#include <iostream>

int main() {
    nlohmann::json content = {
        {"base", {{"x", 1}}},
        {"copy", "$ref:base"}
    };
    RichJson::parse(content);
    std::cout << content.dump() << std::endl;
    return content["copy"]["x"] == 1 ? 0 : 1;
}
