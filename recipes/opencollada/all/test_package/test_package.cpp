#include <COLLADABaseUtils/COLLADABUURI.h>

int main() {
    COLLADABU::URI uri("models/example.dae#visual_scene");
    return !uri.isValid() || uri.getPathFile() != "example.dae" || uri.fragment() != "visual_scene";
}
