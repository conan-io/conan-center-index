#include <imgui.h>

#ifdef DOCKING
    #include <imgui_internal.h>
#endif

#ifdef IMGUI_IMPL_OSX
   #include <imgui_impl_osx.h>
#endif
#ifdef IMGUI_IMPL_METAL
   #include <imgui_impl_metal.h>
#endif

#include <cstdio>

void test_backends() {
#ifdef IMGUI_IMPL_OSX
    ImGui_ImplOSX_Shutdown();
#endif
#ifdef IMGUI_IMPL_METAL
    ImGui_ImplMetal_Shutdown();
#endif
}

int main() {
    printf("IMGUI VERSION: %s\n", IMGUI_VERSION);
    ImGui::CreateContext();
#ifdef DOCKING
    printf("  with docking\n");
#endif
    ImGui::DestroyContext();
    return 0;
}
