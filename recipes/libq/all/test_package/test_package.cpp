#include <cstdlib>
#include <q/lib.hpp>
#include <iostream>


int main(void) {
    q::initialize();
    std::cout << "q initialized correctly" << std::endl;
    q::uninitialize();
    return EXIT_SUCCESS;
}
