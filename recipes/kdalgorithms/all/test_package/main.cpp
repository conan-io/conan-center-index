#include <cstdlib>
#include <iostream>

#include <kdalgorithms/kdalgorithms.h>

int main() {
    auto vec = kdalgorithms::iota(1, 10);
    std::cout << "kdalgorithms::iota: " << vec[0] << "\n";
    return EXIT_SUCCESS;
}
