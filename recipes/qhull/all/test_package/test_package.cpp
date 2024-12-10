#include <libqhullcpp/Qhull.h>

#include <iostream>

int main() {
    orgQhull::Qhull qhull;
    std::cout << "Qhull default hull dimension: " << qhull.hullDimension() << std::endl;
    return 0;
}
