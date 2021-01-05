#include "decimal.hh"

#include <iostream>

int main(int argc, const char *argv[]) {
    if (argc != 3) {
        std::cerr << "Requires 2 arguments\n";
        return 1;
    }
    decimal::Decimal d1(argv[1]);
    decimal::Decimal d2(argv[2]);
    std::cout << d1 << ".pow(" << d2 << ") = " << d1.pow(d2) << "\n";
    return 0;
}
