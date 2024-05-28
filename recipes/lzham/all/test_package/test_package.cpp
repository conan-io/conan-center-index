#include <string>
#include <iostream>

#include <lzham.h>

int main() {
    const std::string version(lzham_z_version());

    std::cout << "lzham version: " << version << std::endl;


    return EXIT_SUCCESS;
}
