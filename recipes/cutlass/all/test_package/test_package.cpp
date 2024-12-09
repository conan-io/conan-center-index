#include <cutlass/version.h>

#include <iostream>

int main() {
    std::cout << "CUTLASS version: " <<
        cutlass::getVersionMajor() << "." <<
        cutlass::getVersionMinor() << "." <<
        cutlass::getVersionPatch() << std::endl;
}
