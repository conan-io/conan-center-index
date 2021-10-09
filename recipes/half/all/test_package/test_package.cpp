#include <half.hpp>

#include <iostream>

int main() {
    half_float::half a(3.4), b(5);
    half_float::half c = a * b;
    c += 3;
    std::cout << c << std::endl;
    return 0;
}
