#include <cstdlib>
#include <iostream>
#include <osgEarth/Map>

int main() {
    osgEarth::initialize();
    std::cout << "osgEarth version: " << osgEarth::getVersion() << std::endl;
    return EXIT_SUCCESS;
}
