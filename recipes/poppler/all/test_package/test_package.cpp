#include "poppler-version.h"

#include <cstdlib>
#include <iostream>

using namespace poppler;

int main(int argc, char **argv) {
    std::cout << "Poppler version: " << version_string() << std::endl;

    return EXIT_SUCCESS;
}
