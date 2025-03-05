#include <iostream>

#include "au/au.hh"
#include "au/io.hh"
#include "au/units/meters.hh"

using namespace au;

int main(void) {
    constexpr auto length = meters(100.0);

    std::cout << length << " == " << length.as(kilo(meters)) << std::endl;

    return EXIT_SUCCESS;
}
