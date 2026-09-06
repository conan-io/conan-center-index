#include <imgui.h>
#include <imgui_node_editor.h>

int main() {
  ImGui::CreateContext();

  auto* editor = ax::NodeEditor::CreateEditor();
  ax::NodeEditor::DestroyEditor(editor);

  ImGui::DestroyContext();

  return 0;
}
