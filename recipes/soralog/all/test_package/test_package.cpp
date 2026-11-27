#include <cstdlib>
#include <iostream>
#include <soralog/soralog.hpp>


int main() {
    std::cout << soralog::libraryName() << std::endl;
    return EXIT_SUCCESS;
}
