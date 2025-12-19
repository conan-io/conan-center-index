#include <iostream>
#include <fbgemm/Fbgemm.h>

int main() {
    std::cout << "Supported CPU?: " << fbgemm::fbgemmSupportedCPU() << std::endl;
    return 0;
}
