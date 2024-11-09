#include <cstdlib>
#include <string>
#include <vector>
#include <iostream>

#include <libfswatch/c++/path_utils.hpp>

int main() {
    std::vector<std::string> directory_children = fsw::get_directory_children(".");
    for (const auto& it : directory_children) {
        std::cout << it << std::endl;
    }

    return 0;
}
