#define SDL_MAIN_HANDLED
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>

int main(int argc, char **argv) {
    printf("SDL3_ttf version: %i", TTF_Version());

    return 0;
}
