#include <ofbx.h>

#include <fstream>
#include <iostream>
#include <vector>

int main(int argc, char **argv) {

    std::vector<ofbx::u8> content(13);
    ofbx::IScene *g_scene = ofbx::load(&content[0], 13, static_cast<ofbx::u64>(ofbx::LoadFlags::TRIANGULATE));

    std::cout << "Test: " << g_scene << std::endl;

    return 0;
}
