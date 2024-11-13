#include <msdfgen.h>
#include <msdfgen-ext.h>

#include <iostream>

int main(int argc, char **argv) {
    msdfgen::FreetypeHandle *ft = msdfgen::initializeFreetype();
    if (ft) {
        std::cout << "Test" << std::endl; // This should be printed
    }
    return 0;
}
