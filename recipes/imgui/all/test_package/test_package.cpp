#include <imgui.h>
#ifdef DOCKING
    #include <imgui_internal.h>
#endif

#include <stdio.h>

int main(int, char**)
{
        printf("IMGUI VERSION: %s\n", IMGUI_VERSION);

#ifdef DOCKING
        auto dockspaceID = ImGui::GetID("MyDockSpace");
        static ImGuiDockNodeFlags dockspace_flags = ImGuiDockNodeFlags_None;
        ImGui::DockSpace(dockspaceID, ImVec2(0.0f, 0.0f), dockspace_flags);
        printf("  with docking\n");
#endif

    return 0;
}
