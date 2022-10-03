#include <cstdlib>
#include <iostream>
#include "package/foobar.hpp"


int main(void) {
    std::cout << "Create a minimal usage for the target project here.\n";
    std::cout << "Avoid big examples, bigger than 100 lines.\n";
    std::cout << "Avoid networking connections.\n";
    std::cout << "Avoid background apps or servers.\n";
    std::cout << "The propose is testing the generated artifacts only.\n";

    foobar.print_version();

    return EXIT_SUCCESS;
}
