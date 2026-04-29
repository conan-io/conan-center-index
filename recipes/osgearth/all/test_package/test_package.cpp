#include <cstdlib>
#include <iostream>
#include <osgEarth/Version>
#include <osgEarth/Capabilities>

int main() {
    std::cout << "osgEarth version: " << osgEarthGetVersion() << std::endl;
    std::cout << "osgEarth SO version: " << osgEarthGetSOVersion() << std::endl;
    std::cout << "osgEarth library name: " << osgEarthGetLibraryName() << std::endl;
    return EXIT_SUCCESS;
}
