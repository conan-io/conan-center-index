
#include <iostream>
#include <assert.h>

#ifdef WITH_BULLET
    #include "Magnum/BulletIntegration/Integration.h"

    void with_bullet() {
        std::cout << "With Bullet\n";
        Magnum::Math::Vector3<btScalar> a{btScalar(1.0), btScalar(2.0), btScalar(3.0)};
        btVector3 b{btScalar(1.0), btScalar(2.0), btScalar(3.0)};
        assert(Magnum::Math::Vector3<btScalar>{b} == a);
    }
#endif

#ifdef WITH_EIGEN
    #include <Eigen/Geometry>
    #include "Magnum/EigenIntegration/Integration.h"

    void with_eigen() {
        std::cout << "With Eigen\n";
        Magnum::Math::Quaternion<float> q{};
        Eigen::Quaternion<float> eq{q.scalar(), q.vector().x(), q.vector().y(), q.vector().z()};
    }
#endif

#ifdef WITH_GLM
    #include "Magnum/Magnum.h"
    #include "Magnum/Math/Matrix3.h"
    #include "Magnum/Math/Matrix4.h"
    #include "Magnum/GlmIntegration/Integration.h"

    void with_glm() {
        std::cout << "With GLM\n";
        Magnum::Math::BoolVector<2> a{0x6};
        glm::bvec2 b{false, true};
        assert(glm::bvec2(a) == b);
    }
#endif

#ifdef WITH_IMGUI
    #include <Magnum/Magnum.h>
    #include <Magnum/Math/Color.h>
    #include "Magnum/ImGuiIntegration/Integration.h"

    void with_imgui() {
        std::cout << "With ImGui\n";
        ImVec2 imVec2{1.1f, 1.2f};
        Magnum::Vector2 vec2(1.1f, 1.2f);
        assert(Magnum::Vector2{imVec2} == vec2);
    }
#endif

int main() {
    #ifdef WITH_BULLET
        with_bullet();
    #endif

    #ifdef WITH_EIGEN
        with_eigen();
    #endif

    #ifdef WITH_GLM
        with_glm();
    #endif

    #ifdef WITH_IMGUI
        with_imgui();
    #endif

    return 0;
}
