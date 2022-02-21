#include "c4/std/std.hpp"
#include "c4/charconv.hpp"

#include <iostream>

auto main( int argc,  char* argv[]) -> int {
    double value;
    c4::from_chars("52.4354", &value);

    std::cout << value << std::endl;

    return 0;
}
