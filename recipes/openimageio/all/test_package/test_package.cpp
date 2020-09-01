#include "OpenImageIO/imageio.h"

#include <iostream>
#include <cstdlib>

int main() {
    std::cout << "imageio version " << OIIO_NAMESPACE::openimageio_version() << "\n";
    return EXIT_SUCCESS;
}
