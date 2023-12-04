#include <iostream>
#include <DecimalNative.hpp>

using namespace epam::deltix::dfp;

int main(void) {
    const Decimal64 number("42");
    std::cout << number << " : " << number.toUnderlying() << std::endl;
    return 0;
}
