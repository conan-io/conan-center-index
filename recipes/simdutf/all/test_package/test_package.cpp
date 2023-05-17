#include "simdutf.h"

#include <iostream>

int main() {
    const char *source = "1234";
    // 4 == strlen(source)
    bool validutf8 = simdutf::validate_utf8(source, 4);
    if (validutf8) {
        std::cout << "valid UTF-8" << std::endl;
    } else {
        std::cerr << "invalid UTF-8" << std::endl;
        return 1;
    }

    return 0;
}
