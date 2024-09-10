#include <iostream>

#include <sail-c++/sail-c++.h>

int main(int argc, char *argv[])
{
    const char* filename = "my-binary.bmp";
    try {
        const sail::image image(filename);
        std::cout << "Size: " << image.width() << std::endl; // Never reached
    } catch (const std::exception& e) {
        std::cerr << "Error - file not found generate: " << e.what() << std::endl;
    }

    return 0;
}
