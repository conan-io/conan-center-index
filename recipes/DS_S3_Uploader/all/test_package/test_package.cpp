#include <cstdlib>
#include <iostream>
#include "DSUploader.h"

int main() {
    DSUploader uploader;

    uploader.configure("dummy_key", "dummy_secret", "dummy_endpoint", "dummy_bucket");

    std::cout << "configure() called successfully." << std::endl;

    return EXIT_SUCCESS;
}
