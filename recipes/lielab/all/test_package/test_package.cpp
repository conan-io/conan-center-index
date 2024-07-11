#include <cstdlib>
#include <iostream>
#include <Lielab.hpp>


int main(void) {
    std::cout << "Lielab v" << Lielab::VERSION << std::endl;
    std::cout << Lielab::AUTHOR << std::endl;
    std::cout << Lielab::LOCATION << std::endl;

    return EXIT_SUCCESS;
}
