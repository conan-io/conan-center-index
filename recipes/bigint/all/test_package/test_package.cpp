#include <BigIntegerLibrary.hh>

#include <iostream>

int main() {
    BigInteger a = 65536;
    std::cout << a << "^8 = " << a * a * a * a * a * a * a * a << std::endl;
    return 0;
}
