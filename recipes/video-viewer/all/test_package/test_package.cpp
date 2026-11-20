#include <cstdlib>
#include "videoviewer/videoviewer.hpp"
#include <iostream>


int main(void) {
    Deltacast::VideoViewer viewer;

    std::cout << "VideoViewer object created successfully!" << std::endl;

    viewer.window_request_close();

    return EXIT_SUCCESS;
}
