#include <cstdlib>

#include <libfswatch/c++/path_utils.hpp>

int main() {
    const auto directory_children = fsw::get_directory_children(".");

    return EXIT_SUCCESS;
}
