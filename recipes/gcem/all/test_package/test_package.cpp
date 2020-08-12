#include <cstdlib>
#include <iostream>

#include <gcem.hpp>

int main()
{
    constexpr int x = 3;
    constexpr double y = 5;
    
    constexpr int r1 = gcem::factorial(x);
    constexpr double r2 = gcem::lgamma(y);
    constexpr double r3 = gcem::pow(y, 0.5);
    constexpr double r4 = gcem::sqrt(y);
    
    std::cout << "factorial(3) == " << r1 << '\n'
    	<< "lgamma(5) == " << r2 << '\n'
    	<< "pow(5, 0.5) == " << r3 << '\n'
    	<< "sqrt(5) == " << r4 << '\n';

    return EXIT_SUCCESS;
}
