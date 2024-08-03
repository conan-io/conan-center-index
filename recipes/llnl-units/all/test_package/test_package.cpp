#include <cstdlib>
#include <iostream>
#include "units/units.hpp"
using namespace units;

int main(void) {
    auto new_unit=m/s;
    auto another=new_unit*s;
    bool test = another == m;
    std::cout << test << std::endl;

    measurement length1=45.0*m;
    measurement length2=20.0*m;
    measurement result=900.0*m*m;
    measurement area=length1*length2;
    bool test2 = area == result;
    std::cout << test2 << std::endl;

    return EXIT_SUCCESS;
}
