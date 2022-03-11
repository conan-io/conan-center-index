#include <decimal.h>

#include <iostream>

int main() {
    dec::decimal<2> value(143125);
    std::cout << "Value #1 is: " << value << std::endl;

    dec::decimal<2> b("0.11");
    value += b;
    std::cout << "Value #2 is: " << value << std::endl;

    value /= 1000;
    std::cout << "Value #3 is: " << value << std::endl;
    return 0;
}
