#include <SDL.h>

#include <stdio.h>

int main(int argc, char* args[]) {
    SDL_version v;
    SDL_GetVersion(&v);
    printf("SDL version %i.%i.%i\n", int(v.major), int(v.minor), int(v.patch));
    return 0;
}
