#include <cstdlib>
#include <iostream>
#include "msdf-atlas-gen/msdf-atlas-gen.h"


int main(void) {
    std::vector<msdfgen::unicode_t> codepoints;
    msdf_atlas::utf8Decode(codepoints, "Conan");
    std::cout << "Codepoints: ";
    for (const auto it : codepoints) {
        std::cout << std::hex << it << " ";
    }
    std::cout << std::endl;
    return EXIT_SUCCESS;
}