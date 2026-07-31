#define SDL_MAIN_HANDLED
#include <SDL3_mixer/SDL_mixer.h>
#include <stdio.h>

int main(void)
{
    printf("SDL3_mixer MIX_Version: %d\n", MIX_Version());
    return 0;
}
