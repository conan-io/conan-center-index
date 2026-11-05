#include <iostream>
#include <cstdlib>
#include <notcurses/notcurses.h>


int main(void) {
    const char* version = notcurses_version();
    std::cout << "Notcurses version: " << version << std::endl;

    return EXIT_SUCCESS;
}
