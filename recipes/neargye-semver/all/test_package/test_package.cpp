#include <iostream>
#include <semver.hpp>

int main() {
    const auto v_default = semver::from_string("0.1.0");
    const auto v1 = semver::from_string("1.4.3");
    const auto v2 = semver::from_string("1.2.4-alpha.10");

    if (v_default.to_string() != "0.1.0" ||
        v1.to_string() != "1.4.3" ||
        v2.to_string() != "1.2.4-alpha.10" ||
        !(v2 < v1)) {
        return 1;
    }

#if SEMVER_VERSION_MAJOR >= 1
    const auto v3 = semver::from_string("1.2.3-rc.1+build.42");
    if (v3.prerelease_tag() != "rc.1" ||
        v3.build_metadata() != "build.42" ||
        v3.without_prerelease().to_string() != "1.2.3+build.42") {
        return 1;
    }
#endif

    std::cout << v1 << '\n';
    std::cout << v2 << '\n';
#if SEMVER_VERSION_MAJOR >= 1
    std::cout << v3 << '\n';
#endif
    return 0;
}
