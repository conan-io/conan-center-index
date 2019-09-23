#include <tiny_obj_loader.h>
#include <vector>
#include <iostream>

int main (void)
{
    tinyobj::attrib_t attrib;
    std::vector<tinyobj::shape_t> shapes;
    std::vector<tinyobj::material_t> materials;
    std::string warn;
    std::string err;
    bool ret = tinyobj::LoadObj(
        &attrib, &shapes, &materials, &warn, &err, "cube.obj");

    if (!warn.empty()) {
        std::cout << "WARN: " << warn << std::endl;
    }

    if (!err.empty()) {
        std::cerr << "ERR: " << err << std::endl;
    }

    if (!ret) {
        std::cerr << "Failed to load/parse .obj" << std::endl;
        return 1;
    }

    return 0;
}
