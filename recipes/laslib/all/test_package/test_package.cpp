#include <iostream>
#include "LASlib/lasreader.hpp"

int main(void) {

    LASreadOpener readOpener;
    readOpener.set_file_name("test.laz");
    LASreader* lasreader = readOpener.open();

    std::cout << "test.laz number of points : " << lasreader->header.number_of_point_records << std::endl;

    return EXIT_SUCCESS;
}
