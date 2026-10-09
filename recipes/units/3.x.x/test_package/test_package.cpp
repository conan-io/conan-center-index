#include <iostream>

#include <units.h>

using namespace units::literals;
using namespace units::length;

int main()
{
    meters<double> a = 3.0_m;
    meters<double> b = 4.0_m;
    meters<double> c = units::sqrt(units::pow<2>(a) + units::pow<2>(b)); // Pythagorean theorem.
    std::cout << c << std::endl;                                         // prints: "5 m"
}
