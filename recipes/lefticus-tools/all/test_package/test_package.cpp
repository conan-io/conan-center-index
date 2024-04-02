#include <cstdlib>
#include <iostream>

#include "lefticus/tools/consteval_invoke.hpp"


constexpr unsigned int Factorial(unsigned int number) {
    return number <= 1 ? number : Factorial(number - 1) * number;
}


int main() {
    std::cout << "Factorial of 3 is: " << lefticus::tools::consteval_invoke(Factorial, 3) << std::endl;
    return EXIT_SUCCESS;
}
