#include <imgui.h>
#include <stdio.h>

int main(int, char**)
{
    ImGuiContext* context =ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();

    ImGuiTextBuffer textBuffer;
    textBuffer.append("Hello, ImGui");

    // Build atlas
    unsigned char* tex_pixels = NULL;
    int tex_w, tex_h;
    io.Fonts->GetTexDataAsRGBA32(&tex_pixels, &tex_w, &tex_h);

    for (int n = 0; n < 50; n++)
    {
        printf("NewFrame() %d\n", n);
        io.DisplaySize = ImVec2(1920, 1080);
        io.DeltaTime = 1.0f / 60.0f;
        ImGui::NewFrame();

        static float f = 0.0f;
        ImGui::Text("Hello, world!");
        ImGui::Text(textBuffer.begin());
        ImGui::SliderFloat("float", &f, 0.0f, 1.0f);
        ImGui::Text("Application average %.3f ms/frame (%.1f FPS)", 1000.0f / io.Framerate, io.Framerate);
        ImGui::ShowDemoWindow(NULL);

        ImGui::Render();
    }

    printf("DestroyContext()\n");
    ImGui::DestroyContext(context);
    return 0;
}
