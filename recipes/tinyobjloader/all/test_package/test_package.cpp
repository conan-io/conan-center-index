#include <tiny_obj_loader.h>

#include <iostream>
#include <string>
#include <vector>

int main(int argc, char **argv)
{
    if (argc < 3) {
        std::cerr << "Need at least two arguments" << std::endl;
        return 1;
    }

#ifdef TINYOBJLOADER_GE_2
    tinyobj::ObjReaderConfig config;
    config.mtl_search_path = argv[2];

    tinyobj::ObjReader reader;
    reader.ParseFromFile(argv[1], config);
#else
    tinyobj::attrib_t attrib;
    std::vector<tinyobj::shape_t> shapes;
    std::vector<tinyobj::material_t> materials;
#ifdef TINYOBJLOADER_GE_1_0_7
    std::string warn;
#endif
    std::string err;
    bool ret = tinyobj::LoadObj(
        &attrib, &shapes, &materials,
#ifdef TINYOBJLOADER_GE_1_0_7
        &warn,
#endif
        &err, argv[1], argv[2]);

#ifdef TINYOBJLOADER_GE_1_0_7
    if (!warn.empty()) {
        std::cout << "WARN: " << warn << std::endl;
    }
#endif

    if (!err.empty()) {
        std::cerr << "ERR: " << err << std::endl;
    }

    if (!ret) {
        std::cerr << "Failed to load/parse .obj" << std::endl;
        return 1;
    }
#endif

    return 0;
}
