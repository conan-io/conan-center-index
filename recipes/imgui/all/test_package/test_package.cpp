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
#else
    printf("  without docking\n");
#endif

#ifdef IMGUI_ENABLE_TEST_ENGINE
    printf("  with test engine\n");
    ImGuiTestEngine *engine = ImGuiTestEngine_CreateContext();
    if (engine == NULL) {
      printf("  Failed to create test engine context\n");
      return -1;
    }
    ImGuiTestEngine_Start(engine, ImGui::GetCurrentContext());
    ImGuiTestEngine_Stop(engine);
    ImGui::DestroyContext();
    ImGuiTestEngine_DestroyContext(engine);
#else
    printf("  without test engine\n");
    ImGui::DestroyContext();
#endif

#ifdef IMGUI_DISABLE_OBSOLETE_FUNCTIONS
    printf("  without obsolete functions\n");
#else
    printf("  with obsolete functions\n");
#endif

#ifdef IMGUI_USE_WCHAR32
    printf("  with wchar32 support\n");
#else
    printf("  without wchar32 support\n");
#endif

    return 0;
}
