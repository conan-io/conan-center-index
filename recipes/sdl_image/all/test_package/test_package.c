#define SDL_MAIN_HANDLED
#include "SDL_image.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    SDL_version compile_version;
    const SDL_version *link_version = IMG_Linked_Version();
    SDL_IMAGE_VERSION(&compile_version);
    printf("SDL2_image compile version: %d.%d.%d\n",
        (int)compile_version.major, (int)compile_version.minor, (int)compile_version.patch);
    printf("SDL2_image link version: %d.%d.%d\n",
        (int)link_version->major, (int)link_version->minor, (int)link_version->patch);
    return EXIT_SUCCESS;
}
