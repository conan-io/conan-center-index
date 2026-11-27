#include <causalontology/canonical.hpp>

#include <iostream>

int main() {
    co::JValue occurrent = co::JValue::makeObject();
    occurrent.set("type", co::JValue::of("occurrent"));
    occurrent.set("label", co::JValue::of("press_button"));
    occurrent.set("category", co::JValue::of("action"));
    const std::string id = co::identify(occurrent);
    std::cout << "identify(press_button) = " << id << std::endl;
    return 0;
}
