#include "config.h"

#include <cstdlib>
#include <iostream>

int main() {
    std::cout << "test_package.cpp: " << "hello world from " PACKAGE_NAME "!\n";
    return EXIT_SUCCESS;
}
