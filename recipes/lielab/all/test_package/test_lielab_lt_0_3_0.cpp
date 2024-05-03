#include <cstdlib>
#include <iostream>
#include "lielab/lielab"


int main(void) {
    std::cout << "Lielab v" << lielab::VERSION << std::endl;
    std::cout << lielab::AUTHOR << std::endl;
    std::cout << lielab::LOCATION << std::endl;

    return EXIT_SUCCESS;
}