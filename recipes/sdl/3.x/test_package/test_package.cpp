#include <SDL3/SDL.h>
#include <iostream>

int main(int argc, char* args[]) {
    auto version = SDL_GetVersion();
    std::cout << "SDL version " << version << std::endl;
    return 0;
}
