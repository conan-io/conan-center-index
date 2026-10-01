#include <imgui.h>
#ifdef DOCKING
    #include <imgui_internal.h>
#endif
#ifdef IMGUI_ENABLE_TEST_ENGINE
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

#ifdef IMGUI_ENABLE_TEST_ENGINE
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

#ifdef IMGUI_DISABLE_OBSOLETE_FUNCTIONS
    printf("  with obsolete functions disabled\n");
#endif

#ifdef IMGUI_USE_WCHAR32
    printf("  with wchar32 support\n");
#endif

    return 0;
}
