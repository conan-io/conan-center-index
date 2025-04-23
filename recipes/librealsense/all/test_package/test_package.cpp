#include <librealsense2/rs.hpp>
#include <librealsense2/rs.h>
#include <iostream>

int main() {
    rs2::context context;
    rs2_error* e = nullptr;
    std::cout << "librealsense2 api version: " << rs2_get_api_version(&e) << "\n";
    return EXIT_SUCCESS;
}
