#include <cstdlib>
#include <iostream>
#include "package/foobar.hpp"


int main(void) {
    std::cout << "Create a minimal usage for the target project here." << std::endl;
    std::cout << "Avoid big examples, bigger than 100 lines" << std::endl;
    std::cout << "Avoid networking connections." << std::endl;
    std::cout << "Avoid background apps or servers." << std::endl;
    std::cout << "The propose is testing the generated artifacts only." << std::endl;

    foobar.print_version();

    return EXIT_SUCCESS;
}
