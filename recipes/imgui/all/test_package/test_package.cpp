#include <imgui.h>
#ifdef DOCKING
    #include <imgui_internal.h>
#endif
#ifdef ENABLE_TEST_ENGINE
#include <imgui_te_engine.h>
#endif

#include <stdio.h>

int main(int, char**)
{
    printf("IMGUI VERSION: %s\n", IMGUI_VERSION);
    ImGui::CreateContext();
#ifdef DOCKING
    printf("  with docking\n");
#endif

#ifdef USE_WCHAR32
    printf("  with wchar32\n");
    static_assert(sizeof(ImWchar) == 4, "ImWchar should be 32-bit when IMGUI_USE_WCHAR32 is defined");
#else
    static_assert(sizeof(ImWchar) == 2, "ImWchar should be 16-bit by default");
#endif

#ifdef ENABLE_TEST_ENGINE
    printf("  with test engine\n");
    ImGuiTestEngine *engine = ImGuiTestEngine_CreateContext();
    if (engine == NULL) {
      printf("  Failed to create test engine context\n");
      return -1;
    }
    ImGui::DestroyContext();
    ImGuiTestEngine_DestroyContext(engine);
#else
    ImGui::DestroyContext();
#endif

    return 0;
}
