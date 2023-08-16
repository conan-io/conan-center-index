#include <fpm/fixed.hpp>
#include <fpm/math.hpp>
#include <fpm/ios.hpp>

#include <iostream>

int main() {
    fpm::fixed_16_16 x {0.0};
    std::cout << "The cosine of " << x << " radians is: " << cos(x) << std::endl;

    return 0;
}
