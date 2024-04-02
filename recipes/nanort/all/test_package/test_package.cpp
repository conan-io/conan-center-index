#include <cstdlib>
#include <iostream>
#include <array>

#include "nanort.h"


int main(void) {
    const std::array<float, 9> vertices = {0.0f, 0.0f, 0.0f,
                                           1.0f, 0.0f, 0.0f,
                                           0.0f, 1.0f, 0.0f};
    const std::array<unsigned int, 3> faces = {0, 1, 2};

    nanort::TriangleMesh<float> triangle_mesh(vertices.data(), faces.data(), sizeof(float) * 3);
    nanort::TriangleSAHPred<float> triangle_pred(vertices.data(), faces.data(), sizeof(float) * 3);

    nanort::BVHAccel<float> accel;
    const auto ret = accel.Build(1, triangle_mesh, triangle_pred);

    if (!ret) {
        std::cerr << "Failed to build BVH" << std::endl;
        return EXIT_FAILURE;
    }

    std::cout << "Successfully built simple BVH with nanort" << std::endl;
    return EXIT_SUCCESS;
}
