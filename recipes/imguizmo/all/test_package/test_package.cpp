#include <imgui.h>
#include <ImGuizmo.h>

int main() {
  float matrix[] = {
    1.0f, 1.0f, 1.0f, 0.5f,
    2.0f, 2.0f, 2.0f, 0.5f,
    3.0f, 3.0f, 3.0f, 0.5f,
    0.0f, 0.0f, 0.0f, 1.0f,
  };
  float matrixTranslation[3], matrixRotation[3], matrixScale[3];
  ImGuizmo::DecomposeMatrixToComponents(matrix, matrixTranslation, matrixRotation, matrixScale);

  return 0;
}
