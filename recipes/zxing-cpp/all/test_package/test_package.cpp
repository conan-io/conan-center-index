#include "ZXing/ZXingC.h"

#include <cstdlib>
#include <iostream>


int main() {

    std::cout << "ZXing version: " << ZXing_Version() << std::endl;

    return EXIT_SUCCESS;
}
