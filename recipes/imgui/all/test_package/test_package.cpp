#include <imgui.h>
#ifdef DOCKING
    #include <imgui_internal.h>
#endif

#include <stdio.h>

int main(int, char**)
{
        printf("IMGUI VERSION: %s\n", IMGUI_VERSION);

#ifdef DOCKING
        printf("  with docking\n");
#endif

    return 0;
}
