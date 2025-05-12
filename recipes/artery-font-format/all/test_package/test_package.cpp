#include <iostream>

#include <artery-font/std-artery-font.h>

int main(int argc, char *argv[]) {
    auto list = artery_font::StdList<int>(5);
    std::cout << "There are " << list.length() << " elements in the list" << std::endl;
    return EXIT_SUCCESS;
}
