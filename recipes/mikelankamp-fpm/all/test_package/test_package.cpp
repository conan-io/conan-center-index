#include <fpm/fixed.hpp>
#include <fpm/math.hpp>
#include <fpm/ios.hpp>

#include <iostream>

int main() {
    std::cout << "Please input a number: ";
    fpm::fixed_16_16 x;
    std::cin >> x;
    std::cout << "The cosine of " << x << " radians is: " << cos(x) << std::endl;

    return 0;
}
