#include <iostream>
#include "google/type/color.pb.h"

int main() {
    std::cout << "Conan - test package for googleapis\n";

    google::type::Color c;
    c.set_red(255);
    c.set_blue(255);

    std::cout << c.DebugString();

    return 0;
}
