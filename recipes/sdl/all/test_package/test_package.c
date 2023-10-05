#include <SDL.h>

#include <stdio.h>

int main(int argc, char* args[]) {
    SDL_version v;
    SDL_GetVersion(&v);
    printf("SDL version %u.%u.%u\n", v.major, v.minor, v.patch);
    return 0;
}
