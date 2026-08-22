#include <iostream>
#include <pmp/surface_mesh.h>

int main() {
    try {
        pmp::SurfaceMesh mesh;
        std::cout << "PMP library loaded and SurfaceMesh instantiated successfully\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }
}