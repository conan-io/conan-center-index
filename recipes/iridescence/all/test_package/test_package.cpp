#include <glk/primitives/primitives.hpp>
#include <guik/viewer/light_viewer.hpp>

void test() {
  auto viewer = guik::LightViewer::instance();

  float angle = 0.0f;

  viewer->register_ui_callback("ui", [&]() {
    ImGui::DragFloat("Angle", &angle, 0.01f);

    if (ImGui::Button("Close")) {
      viewer->close();
    }
  });

  while (viewer->spin_once()) {
    Eigen::AngleAxisf transform(angle, Eigen::Vector3f::UnitZ());
    viewer->update_drawable("sphere", glk::Primitives::sphere(), guik::Rainbow(transform));
    viewer->update_drawable("wire_sphere", glk::Primitives::wire_sphere(), guik::FlatColor({0.1f, 0.7f, 1.0f, 1.0f}, transform));
  }
}

int main(int argc, char* argv[]) {
  if(argc > 1) {
    test();
  }
  return 0;
}
