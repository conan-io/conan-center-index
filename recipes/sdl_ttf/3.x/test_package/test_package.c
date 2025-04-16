#define SDL_MAIN_HANDLED
#include <SDL3_ttf/SDL_ttf.h>
#include <stdio.h>

int main(int argc, char **argv) {
    if (!TTF_Init()) {
        fprintf(stderr, "Failed to initialize TTF: %s\n", SDL_GetError());
        return 1;
    }

    printf("SDL3_ttf is working!\n");

    return 0;
}
