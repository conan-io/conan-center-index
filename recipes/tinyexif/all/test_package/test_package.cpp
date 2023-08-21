#include <iostream>
#include "TinyEXIF.h"

int main() {
    TinyEXIF::EXIFInfo exif;

    std::cout << exif.Fields << std::endl;

    return 0;
}
