#include <cstdlib>
#include <iostream>
#include "SDL_image.h"

int main(int argc, char *argv[])
{
    SDL_version compile_version;
    const SDL_version * link_version=IMG_Linked_Version();
    SDL_IMAGE_VERSION(&compile_version);
    std::cout << "SDL2_image compile version: " <<
        int(compile_version.major) << "." <<
        int(compile_version.minor) << "." <<
        int(compile_version.patch) << std::endl;
    std::cout << "SDL2_image link version: " <<
        int(link_version->major) << "." <<
        int(link_version->minor) << "." <<
        int(link_version->patch) << std::endl;
    return EXIT_SUCCESS;
}
