#define SDL_MAIN_HANDLED
#include <SDL3_shadercross/SDL_shadercross.h>
#include <stdio.h>

int main(void)
{
    if (!SDL_ShaderCross_Init()) {
        return 1;
    }
    printf("SDL_shadercross SPIR-V formats: 0x%x\n", (unsigned)SDL_ShaderCross_GetSPIRVShaderFormats());
    SDL_ShaderCross_Quit();
    return 0;
}
