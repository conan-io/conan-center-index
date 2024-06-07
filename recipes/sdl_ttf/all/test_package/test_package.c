#define SDL_MAIN_HANDLED
#include <SDL_ttf.h>

#include <stdio.h>

int main(int argc, char **argv) {
    if (TTF_Init() == -1) {
        fprintf(stderr, "Failed to initialize TTF: %s\n", SDL_GetError());
        return 1;
    }

    printf("SDL2_ttf is working!\n");

    return 0;
}
