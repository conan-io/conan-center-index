#include "fcarouge/kalman.hpp"
#include <iostream>

int main() {
    using namespace fcarouge;
    kalman filter{state{60.}, output<double>, estimate_uncertainty{225.}, output_uncertainty{25.}};
    filter.update(42);
    std::cout << "Estimation: " << filter.x() << std::endl;
}
