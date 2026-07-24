#include <iostream>
#include <semver.hpp>

int main() {
    const auto v1 = semver::from_string("1.4.3");
    const auto v2 = semver::from_string("1.2.4-alpha.10");

    std::cout << v1 << '\n';
    std::cout << v2 << '\n';
    return 0;
}
