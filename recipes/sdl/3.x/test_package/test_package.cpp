#include <SDL3/SDL_version.h>
#include <iostream>

int main(int argc, char* args[]) {
    auto ver = SDL_GetVersion();
    std::cout << "SDL version " << SDL_VERSIONNUM_MAJOR(ver) << "." << SDL_VERSIONNUM_MINOR(ver) << "." << SDL_VERSIONNUM_MICRO(ver) << std::endl;
    return 0;
}
