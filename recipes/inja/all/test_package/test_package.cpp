#include <iostream>

#include <inja/inja.hpp>

int main()
{
    nlohmann::json data;
    data["name"] = "world";
    std::cout << inja::render("Hello {{ name }}!", data) << "\n";
}
