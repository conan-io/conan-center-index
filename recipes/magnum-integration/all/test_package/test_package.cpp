
#include <iostream>

int main() {
    #ifdef WITH_BULLET
        std::cout << "With Bullet\n";
    #endif
    #ifdef WITH_DART
        std::cout << "With Dart\n";
    #endif
    #ifdef WITH_EIGEN
        std::cout << "With Eigen\n";
    #endif
    #ifdef WITH_GLM
        std::cout << "With Glm\n";
    #endif
    #ifdef WITH_IMGUI
        std::cout << "With ImGui\n";
    #endif
    #ifdef WITH_OVR
        std::cout << "With Ovr\n";
    #endif
    return 0;
}
