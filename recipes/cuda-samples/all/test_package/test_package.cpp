#include <cstdlib>
#include <iostream>

// One of the few non-CUDA-specific headers in the CUDA Samples.
#include "helper_string.h"


int main() {
    char file[] = "hello_world.jpg";
    char *ext = NULL;
    getFileExtension(file, &ext);

    std::cout << "getFileExtension(\"" << file << "\") returned \"" << ext << "\"." << std::endl;

    return EXIT_SUCCESS;
}
