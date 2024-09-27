#include <iostream>

#include "au/au.hh"
#include "au/io.hh"
#include "au/units/meters.hh"

using namespace au;

int main(void) {
    constexpr auto lenght = meters(100.0);

    std::cout << lenght << " == " << lenght.in(kilo(meters)) <<" km" << std::endl;

    return EXIT_SUCCESS;
}
