#include <trng/yarn2.hpp>
#include <trng/uniform01_dist.hpp>
#include <iostream>

int main() {
    trng::yarn2 r;
    trng::uniform01_dist<double> u;
    const double val{u(r)};
    std::cout << "TRNG generated random value: " << val << std::endl;
    return 0;
}
