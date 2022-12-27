#include <SDL.h>
#include <iostream>

int main(int argc, char *argv[])
{
    SDL_version v;
    SDL_GetVersion(&v);
    std::cout << "SDL version " << int(v.major) << "." << int(v.minor) << "." << int(v.patch) << std::endl;
}
