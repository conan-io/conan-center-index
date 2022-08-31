#include <iostream>
#include <semver200.h>

int main(void) {
    auto ver{version::Semver200_version("1.0.1+22910")};
    std::cout << "Parsed Major: " << (ver.major)() << std::endl;
    return 0;
}
