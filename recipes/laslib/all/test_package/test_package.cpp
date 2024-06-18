#include <iostream>
#include "LASlib/lasreader.hpp"

int main(void) {

    LASreadOpener readOpener;
    readOpener.set_file_name("test_package.cpp");

    std::cout << "Test: " << readOpener.active() << std::endl;

    return EXIT_SUCCESS;
}
