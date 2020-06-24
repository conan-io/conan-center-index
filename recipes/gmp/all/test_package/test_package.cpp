#include <gmpxx.h>

#include <cstdlib>
#include <iostream>

int main (void) {
    mpz_class a("1234");
    mpz_class b("4321");

    mpz_class c = a + b;
    std::cout << a << " + " << b << " = " << c << "\n";

    return EXIT_SUCCESS;
}
