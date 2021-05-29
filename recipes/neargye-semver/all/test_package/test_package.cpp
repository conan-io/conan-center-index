#include <iostream>
#include <semver.hpp>

int main() {
    constexpr semver::version v_default;
    std::cout << v_default << std::endl; // 0.1.0

    constexpr semver::version v1{1, 4, 3};
    constexpr semver::version v2{"1.2.4-alpha.10"};
    std::cout << v1 << std::endl; // 1.4.3
    std::cout << v2 << std::endl; // 1.2.4-alpha.10

    semver::version v_s;
    v_s.from_string("1.2.3-rc.1");
    std::string s1 = v_s.to_string();
    std::cout << s1 << std::endl; // 1.2.3-rc.1
    v_s.prerelease_number = 0;
    std::string s2 = v_s.to_string();
    std::cout << s2 << std::endl; // 1.2.3-rc

    return 0;
}
