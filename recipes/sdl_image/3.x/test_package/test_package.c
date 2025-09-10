#define SDL_MAIN_HANDLED
#include "SDL3_image/SDL_image.h"
#include <stdio.h>

int main(int argc, char *argv[])
{
    printf("SDL_image Version: %i\n", IMG_Version());
}
