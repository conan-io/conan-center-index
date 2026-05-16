#include <cenginel/cenginel.hpp>
#include <iostream>

int main() {
    using namespace cenginel;
    matrix_t<double> P(2, 2);
    P << 0.9, 0.1, 0.5, 0.5;
    markov_chain<double> mc(P);
    auto pi = mc.stationary_distribution();
    std::cout << "Stationary: " << pi.transpose() << std::endl;
    return 0;
}
