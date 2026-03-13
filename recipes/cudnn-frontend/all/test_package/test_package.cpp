#include <cudnn_frontend_version.h>

#include <iostream>

int main() {
    std::cout << "CuDNN Frontend version: " <<
        CUDNN_FRONTEND_MAJOR_VERSION << "." <<
        CUDNN_FRONTEND_MINOR_VERSION << "." <<
        CUDNN_FRONTEND_PATCH_VERSION << std::endl;
}
