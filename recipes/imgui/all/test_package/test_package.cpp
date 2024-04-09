#include <imgui.h>
#ifdef DOCKING
    #include <imgui_internal.h>
#endif

#include <stdio.h>

int main(int, char**)
{
    printf("IMGUI VERSION: %s\n", IMGUI_VERSION);
    ImGui::CreateContext();
#ifdef DOCKING
    printf("  with docking\n");
#endif
    ImGui::DestroyContext();
    return 0;
}
