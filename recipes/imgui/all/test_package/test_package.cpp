#include <imgui.h>

#ifdef DOCKING
    #include <imgui_internal.h>
#endif

#ifdef IMGUI_IMPL_ALLEGRO5
    #include <imgui_impl_allegro5.h>
#endif
#ifdef IMGUI_IMPL_ANDROID
    #include <imgui_impl_android.h>
#endif
#ifdef IMGUI_IMPL_DX9
    #include <imgui_impl_dx9.h>
#endif
#ifdef IMGUI_IMPL_DX10
    #include <imgui_impl_dx10.h>
#endif
#ifdef IMGUI_IMPL_DX11
    #include <imgui_impl_dx11.h>
#endif
#ifdef IMGUI_IMPL_DX12
    #include <imgui_impl_dx12.h>
#endif
#ifdef IMGUI_IMPL_GLFW
    #include <imgui_impl_glfw.h>
#endif
#ifdef IMGUI_IMPL_GLUT
    #include <imgui_impl_glut.h>
#endif
#ifdef IMGUI_IMPL_OPENGL2
    #include <imgui_impl_opengl2.h>
#endif
#ifdef IMGUI_IMPL_OPENGL3
    #include <imgui_impl_opengl3.h>
#endif
#ifdef IMGUI_IMPL_SDL2
    #include <imgui_impl_sdl2.h>
#endif
#ifdef IMGUI_IMPL_SDLRENDERER2
    #include <imgui_impl_sdlrenderer2.h>
#endif
#ifdef IMGUI_IMPL_SDLRENDERER3
    #include <imgui_impl_sdlrenderer3.h>
#endif
#ifdef IMGUI_IMPL_VULKAN
    #include <imgui_impl_vulkan.h>
#endif
#ifdef IMGUI_IMPL_WIN32
    #include <imgui_impl_win32.h>
#endif
#ifdef IMGUI_IMPL_WGPU
    #include <imgui_impl_wgpu.h>
#endif

#include <cstdio>

void test_backends() {
#ifdef IMGUI_IMPL_ALLEGRO5
    ImGui_ImplAllegro5_Shutdown();
#endif
#ifdef IMGUI_IMPL_ANDROID
    ImGui_ImplAndroid_Shutdown();
#endif
#ifdef IMGUI_IMPL_DX9
    ImGui_ImplDX9_Shutdown();
#endif
#ifdef IMGUI_IMPL_DX10
    ImGui_ImplDX10_Shutdown();
#endif
#ifdef IMGUI_IMPL_DX11
    ImGui_ImplDX11_Shutdown();
#endif
#ifdef IMGUI_IMPL_DX12
    ImGui_ImplDX12_Shutdown();
#endif
#ifdef IMGUI_IMPL_GLFW
    ImGui_ImplGlfw_Shutdown();
#endif
#ifdef IMGUI_IMPL_GLUT
    ImGui_ImplGLUT_Shutdown();
#endif
#ifdef IMGUI_IMPL_OPENGL2
    ImGui_ImplOpenGL2_Shutdown();
#endif
#ifdef IMGUI_IMPL_OPENGL3
    ImGui_ImplOpenGL3_Shutdown();
#endif
#ifdef IMGUI_IMPL_SDL2
    ImGui_ImplSDL2_Shutdown();
#endif
#ifdef IMGUI_IMPL_SDLRENDERER2
    ImGui_ImplSDLRenderer2_Shutdown();
#endif
#ifdef IMGUI_IMPL_SDLRENDERER3
    ImGui_ImplSDLRenderer3_Shutdown();
#endif
#ifdef IMGUI_IMPL_VULKAN
    ImGui_ImplVulkan_Shutdown();
#endif
#ifdef IMGUI_IMPL_WIN32
    ImGui_ImplWin32_Shutdown();
#endif
#ifdef IMGUI_IMPL_WGPU
    ImGui_ImplWGPU_Shutdown();
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
