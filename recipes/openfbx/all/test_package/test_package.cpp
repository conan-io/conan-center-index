#include <ofbx.h>

#include <fstream>
#include <iostream>
#include <vector>

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Need at least one argument" << std::endl;
        return -1;
    }

    std::ifstream in_file(argv[1], std::ios::binary);
    in_file.seekg(0, std::ios::end);
    int file_size = static_cast<int>(in_file.tellg());
    std::vector<ofbx::u8> content(file_size);

    ofbx::IScene *g_scene = ofbx::load(&content[0], file_size, static_cast<ofbx::u64>(ofbx::LoadFlags::TRIANGULATE));

    return 0;
}
